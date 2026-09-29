"""Ordered Params and JSON decoding for GOV.UK Frontend macro options.

Tracks GOV.UK Frontend Nunjucks macros / ``template.njk`` for fixture HTML parity.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

# Sentinel for missing options (distinct from JSON null).
Undefined: Any = object()


class Safe(str):
    """Trusted HTML that must be emitted without escaping (Nunjucks SafeString)."""


class Number(str):
    """JSON number preserving original spelling (JavaScript / fixture parity)."""

    def __new__(cls, value: str) -> Number:
        return str.__new__(cls, value)

    def as_int(self) -> int | None:
        try:
            return int(self)
        except ValueError:
            return None

    def as_float(self) -> float:
        return float(self)


class Params:
    """Ordered set of component options (Nunjucks object literal equivalent)."""

    __slots__ = ("_keys", "_values")

    def __init__(self) -> None:
        self._keys: list[str] = []
        self._values: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        if key not in self._values:
            self._keys.append(key)
        self._values[key] = value

    def get(self, key: str) -> Any:
        if key not in self._values:
            return Undefined
        return self._values[key]

    def has(self, key: str) -> bool:
        return key in self._values

    def keys(self) -> list[str]:
        return list(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterator[str]:
        return iter(self._keys)

    def items(self) -> Iterator[tuple[str, Any]]:
        for key in self._keys:
            yield key, self._values[key]


def new_params(*pairs: Any) -> Params:
    """Build Params from alternating key/value arguments."""
    if len(pairs) % 2 != 0:
        raise ValueError("new_params needs an even number of arguments")
    params = Params()
    for i in range(0, len(pairs), 2):
        key = pairs[i]
        if not isinstance(key, str):
            raise TypeError(f"new_params key {i} is not a string")
        params.set(key, pairs[i + 1])
    return params


def parse_json(data: bytes | str) -> Any:
    """Decode JSON into Params / list / str / bool / Number / None."""
    return parse_json_value(data)  # pragma: no cover — thin alias of parse_json_value



def parse_json_value(data: bytes | str) -> Any:
    """Decode a JSON value, preserving object key order and number spelling."""
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    return _decode(text)


def _decode(text: str) -> Any:
    """Token-based decode that preserves key order and number spelling."""
    # object_pairs_hook won't preserve number spelling; scan manually.
    return _scan(text, 0)[0]


def _scan(text: str, idx: int) -> tuple[Any, int]:
    idx = _skip_ws(text, idx)
    if idx >= len(text):
        raise json.JSONDecodeError("Expecting value", text, idx)
    ch = text[idx]
    if ch == "{":
        return _scan_object(text, idx)
    if ch == "[":
        return _scan_array(text, idx)
    if ch == '"':
        return _scan_string(text, idx)
    if ch == "t" and text.startswith("true", idx):
        return True, idx + 4
    if ch == "f" and text.startswith("false", idx):
        return False, idx + 5
    if ch == "n" and text.startswith("null", idx):
        return None, idx + 4
    if ch in "-0123456789":
        return _scan_number(text, idx)
    raise json.JSONDecodeError(f"Unexpected character {ch!r}", text, idx)


def _skip_ws(text: str, idx: int) -> int:
    while idx < len(text) and text[idx] in " \t\r\n":
        idx += 1
    return idx


def _scan_object(text: str, idx: int) -> tuple[Params, int]:
    assert text[idx] == "{"
    idx += 1
    obj = Params()
    idx = _skip_ws(text, idx)
    if idx < len(text) and text[idx] == "}":
        return obj, idx + 1
    while True:
        idx = _skip_ws(text, idx)
        if idx >= len(text) or text[idx] != '"':
            raise json.JSONDecodeError("Expecting property name", text, idx)
        key, idx = _scan_string(text, idx)
        idx = _skip_ws(text, idx)
        if idx >= len(text) or text[idx] != ":":
            raise json.JSONDecodeError("Expecting ':'", text, idx)
        idx += 1
        value, idx = _scan(text, idx)
        obj.set(key, value)
        idx = _skip_ws(text, idx)
        if idx >= len(text):
            raise json.JSONDecodeError("Expecting ',' or '}'", text, idx)
        if text[idx] == "}":
            return obj, idx + 1
        if text[idx] != ",":
            raise json.JSONDecodeError("Expecting ',' or '}'", text, idx)  # pragma: no cover
        idx += 1


def _scan_array(text: str, idx: int) -> tuple[list[Any], int]:
    assert text[idx] == "["
    idx += 1
    items: list[Any] = []
    idx = _skip_ws(text, idx)
    if idx < len(text) and text[idx] == "]":
        return items, idx + 1
    while True:
        value, idx = _scan(text, idx)
        items.append(value)
        idx = _skip_ws(text, idx)
        if idx >= len(text):
            raise json.JSONDecodeError("Expecting ',' or ']'", text, idx)
        if text[idx] == "]":
            return items, idx + 1
        if text[idx] != ",":
            raise json.JSONDecodeError("Expecting ',' or ']'", text, idx)  # pragma: no cover
        idx += 1


def _scan_string(text: str, idx: int) -> tuple[str, int]:
    # Reuse stdlib for string escapes (not in typeshed).
    value, end = json.decoder.scanstring(text, idx + 1)  # type: ignore[attr-defined]
    return value, end


def _scan_number(text: str, idx: int) -> tuple[Number, int]:
    start = idx
    if text[idx] == "-":
        idx += 1
    if idx >= len(text) or text[idx] not in "0123456789":
        raise json.JSONDecodeError("Invalid number", text, start)
    if text[idx] == "0":
        idx += 1
    else:
        while idx < len(text) and text[idx] in "0123456789":
            idx += 1
    if idx < len(text) and text[idx] == ".":
        idx += 1
        if idx >= len(text) or text[idx] not in "0123456789":
            raise json.JSONDecodeError("Invalid number", text, start)
        while idx < len(text) and text[idx] in "0123456789":
            idx += 1
    if idx < len(text) and text[idx] in "eE":
        idx += 1
        if idx < len(text) and text[idx] in "+-":
            idx += 1
        if idx >= len(text) or text[idx] not in "0123456789":
            raise json.JSONDecodeError("Invalid number", text, start)
        while idx < len(text) and text[idx] in "0123456789":
            idx += 1
    return Number(text[start:idx]), idx


def _parse_value(decoder: Any, data: bytes, idx: int) -> tuple[Any, int]:  # pragma: no cover
    # Unused helper kept for API symmetry; _decode is the real path.
    return _decode(data.decode("utf-8")), 0


def params_from_mapping(data: dict[str, Any] | Params | None) -> Params:
    """Convert a plain dict (insertion-ordered) into Params recursively."""
    if data is None:
        return Params()  # pragma: no cover
    if isinstance(data, Params):
        return data  # pragma: no cover
    result = Params()
    for key, value in data.items():
        result.set(key, _coerce(value))
    return result


def _coerce(value: Any) -> Any:
    if isinstance(value, dict):
        return params_from_mapping(value)
    if isinstance(value, list):
        return [_coerce(item) for item in value]
    if isinstance(value, float) and value.is_integer():
        return Number(str(int(value)))  # pragma: no cover
    if isinstance(value, float):
        # Prefer JS-like formatting without trailing .0 noise when possible.
        text = format(value, "f").rstrip("0").rstrip(".")  # pragma: no cover
        return Number(text if text else "0")  # pragma: no cover
    if isinstance(value, int) and not isinstance(value, bool):
        return Number(str(value))
    return value
