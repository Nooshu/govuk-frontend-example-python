# GOV.UK Frontend example (Python / Django)

> [!WARNING]
> 🚨 **Example repository only**
>
> This repository was created as a demonstration and will not be actively maintained or supported. It is not an official UK government project and is not endorsed, maintained, or supported by any UK government department, the Government Digital Service (GDS), or the GOV.UK Design System team.
>
> You are welcome to fork this repository and adapt, use, and maintain it within your own department or organisation. However, I will not be providing ongoing maintenance, updates, security fixes, or technical support.
>
> Use this code at your own risk. You are responsible for reviewing, testing, securing, maintaining, and ensuring the suitability of the code before using it in any service or production environment. I accept no responsibility or liability for any loss, damage, security issue, service failure, or other consequence resulting from its use.
>
> This repository is released under the MIT Licence. See the [LICENSE](LICENSE) file for the full licence terms.

**GDS-compliant** government frontend example: **Python 3.13 + Django 5.2** generates HTML; **[GOV.UK Frontend](https://frontend.design-system.service.gov.uk/)** **6.5.1** is the only UI library. Native Python renderers track Frontend macros and match every official fixture. **No** React/Vue/Angular/Svelte for UI.

## Quick start

1. Install **[uv](https://docs.astral.sh/uv/getting-started/installation/)** (Python package manager) if you do not have it:

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source "$HOME/.local/bin/env"   # or open a new terminal
   ```

2. Install dependencies and start the service:

   ```sh
   npm ci
   uv sync --all-groups
   npm start
   ```

`npm start` builds the Sass stylesheet and runs Django. If `.venv` is missing, it runs `uv sync` for you (when `uv` is available). Then open <http://127.0.0.1:8000>.

Journey and docs: [`docs/example-service.md`](docs/example-service.md). Deploy: [`docs/deploying-on-render.md`](docs/deploying-on-render.md).

## Checks

```sh
uv run pytest -q -o addopts=          # health, journey, catalogue, fixture parity
uv run pytest                         # + 100% coverage gate
npm test                              # baseline + Sass (Node)
npm run verify:docs
```

## Stack

This repository is the **Python / Django** example. Component HTML is generated natively in Python; pages and forms use Django.

## Priorities

Frontend web performance → frontend security → reduced maintenance → accessibility → inclusive design.

## Who should read what

| You are…            | Start here                                                                                                                                                     |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Human developer** | [`docs/onboarding.md`](docs/onboarding.md) → [`CONTRIBUTING.md`](CONTRIBUTING.md) → [`docs/`](docs/README.md)                                                  |
| **AI coding agent** | [`AGENTS.md`](AGENTS.md) → [`.cursor/skills/gds-compliant-frontend/`](.cursor/skills/gds-compliant-frontend/SKILL.md) → playbooks in [`docs/`](docs/README.md) |

Stack detail: [`docs/tech-stack.md`](docs/tech-stack.md).

## Licence and security

- Code in this repository: [MIT License](LICENSE)
- How to report vulnerabilities: [SECURITY.md](SECURITY.md)
- GOV.UK Design System and Frontend are maintained by GDS; Crown copyright / OGL apply to GOV.UK content patterns as documented on GOV.UK.
