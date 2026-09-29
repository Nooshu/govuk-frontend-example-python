"""Nunjucks-parity filters: escape, indent, length, and related helpers.

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

from typing import Any

from .params import Number, Params, Safe, Undefined

# Mirrors Nunjucks' escape map, backslash included.
_ESCAPES = (
    ("&", "&amp;"),
    ('"', "&quot;"),
    ("'", "&#39;"),
    ("<", "&lt;"),
    (">", "&gt;"),
    ("\\", "&#92;"),
)


def escape(text: str) -> str:
    """Nunjucks' escape filter for a plain string."""
    result = text
    for old, new in _ESCAPES:
        result = result.replace(old, new)
    return result


def get(value: Any, *names: str) -> Any:
    """Walk a chain of option names; return Undefined when the chain leaves an object."""
    for name in names:
        if not isinstance(value, Params):
            return Undefined
        value = value.get(name)
    return value


def items(value: Any) -> list[Any]:
    """Return value as a list, or [] when it is not an array."""
    if isinstance(value, list):
        return value
    return []


def at(value: Any, index: int) -> Any:
    """Return the index'th element of an array option, or Undefined when out of range."""
    list_ = items(value)
    if index < 0 or index >= len(list_):
        return Undefined
    return list_[index]


def truthy(value: Any) -> bool:
    """JavaScript truthiness (empty list/Params are truthy)."""
    if value is None or is_undefined(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, Number):
        try:
            return float(value) != 0
        except ValueError:
            return False
    if isinstance(value, str):
        return value != ""
    # Empty arrays and objects are truthy in JS / Nunjucks.
    return True


def is_undefined(value: Any) -> bool:
    """Report whether an option was never supplied (identity with Undefined)."""
    return value is Undefined


def str_value(value: Any) -> str:
    """Convert a value to the string JavaScript would produce, before escaping."""
    if value is None or is_undefined(value):
        return ""
    if isinstance(value, Safe):
        return str.__str__(value)
    if isinstance(value, Number):
        return format_number(value)
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ",".join(str_value(item) for item in value)
    return "[object Object]"


# Alias for call sites that expect a short name (``str`` is reserved).
str_ = str_value


def format_number(value: Number) -> str:
    """Render a JSON number the way JavaScript prints it (fixture parity)."""
    text = str.__str__(value)
    try:
        return str(int(text, 10))
    except ValueError:
        pass
    try:
        # Match strconv.FormatFloat(f, 'f', -1, 64).
        return f"{float(text):.16f}".rstrip("0").rstrip(".") or "0"
    except ValueError:
        return text


def out(value: Any) -> str:
    """Render a value for a ``{{ }}`` expression: Safe passes through, else escape."""
    if isinstance(value, Safe):
        return str.__str__(value)
    return escape(str_value(value))


def trim(text: str) -> str:
    """Nunjucks' trim filter."""
    return text.strip()


def indent(text: str, width: int, first: bool) -> str:
    """Prefix every line with width spaces, skipping the first unless first is True."""
    if text == "":
        return ""
    padding = " " * width
    lines = text.split("\n")
    for i in range(len(lines)):
        if i == 0 and not first:
            continue
        lines[i] = padding + lines[i]
    return "\n".join(lines)


def def_(value: Any, fallback: Any) -> Any:
    """Nunjucks' ``default(fallback)``: only when the option is undefined."""
    if is_undefined(value):
        return fallback
    return value


def def_truthy(value: Any, fallback: Any) -> Any:
    """Nunjucks' ``default(fallback, true)``: also replaces falsy values."""
    if truthy(value):
        return value
    return fallback


def length(value: Any) -> int:
    """Nunjucks' length filter."""
    if value is None or is_undefined(value):
        return 0
    if isinstance(value, bool):
        return 0
    if isinstance(value, list):
        return len(value)
    if isinstance(value, Params):
        return len(value)
    if isinstance(value, Safe):
        return len(str.__str__(value))
    if isinstance(value, str):
        return len(value)
    return 0


def loose_eq(left: Any, right: Any) -> bool:
    """JavaScript ``==`` for the value kinds the macros compare."""
    left_nil = left is None or is_undefined(left)
    right_nil = right is None or is_undefined(right)
    if left_nil or right_nil:
        return left_nil and right_nil

    left_is_bool = isinstance(left, bool)
    right_is_bool = isinstance(right, bool)
    if left_is_bool and right_is_bool:
        return bool(left == right)
    if left_is_bool:
        return loose_eq(_bool_to_number(left), right)
    if right_is_bool:
        return loose_eq(left, _bool_to_number(right))  # pragma: no cover

    left_is_number = isinstance(left, Number)
    right_is_number = isinstance(right, Number)
    if left_is_number and right_is_number:
        return _numeric(str.__str__(left)) == _numeric(str.__str__(right))
    if left_is_number:
        return _same_number(str.__str__(left), str_value(right))
    if right_is_number:
        return _same_number(str_value(left), str.__str__(right))

    return str_value(left) == str_value(right)


def strict_eq(left: Any, right: Any) -> bool:
    """JavaScript ``===``."""
    if is_undefined(left) or is_undefined(right):
        return is_undefined(left) and is_undefined(right)
    if left is None or right is None:
        return left is None and right is None

    left_is_number = isinstance(left, Number)
    right_is_number = isinstance(right, Number)
    if left_is_number != right_is_number:
        return False
    if left_is_number:
        return _numeric(str.__str__(left)) == _numeric(str.__str__(right))

    if isinstance(left, bool):
        return isinstance(right, bool) and left == right
    if isinstance(left, str) and not isinstance(left, Number):
        return (
            isinstance(right, str)
            and not isinstance(right, Number)
            and left == right
        )
    return bool(left == right)


def contains(needle: Any, haystack: Any) -> bool:
    """Nunjucks ``in`` operator."""
    if isinstance(haystack, Safe):
        return str_value(needle) in str.__str__(haystack)
    if isinstance(haystack, str) and not isinstance(haystack, Number):
        return str_value(needle) in haystack
    if isinstance(haystack, list):
        return any(strict_eq(needle, item) for item in haystack)
    if isinstance(haystack, Params):
        return haystack.has(str_value(needle))
    return False


def concat_if(prefix: str, value: Any) -> str:
    """``(" " + option if option)`` idiom — missing option contributes nothing."""
    if not truthy(value):
        return ""
    return prefix + str_value(value)


def heading(level: Any, fallback: str) -> str:
    """Render a heading level option, falling back when not set."""
    if truthy(level):
        return str_value(level)
    return fallback


def _bool_to_number(value: bool) -> Number:
    return Number("1" if value else "0")


def _numeric(text: str) -> float:
    try:
        return float(text)
    except ValueError:  # pragma: no cover
        return 0.0  # pragma: no cover


def _same_number(left: str, right: str) -> bool:
    trimmed = right.strip()
    if trimmed == "":
        trimmed = "0"
    try:
        value = float(trimmed)
    except ValueError:
        return False
    return _numeric(left) == value
