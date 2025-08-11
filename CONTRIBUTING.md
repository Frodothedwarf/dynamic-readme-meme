# Contributing to **dynamic-readme-meme**

Thanks for taking the time to help! This project fetches memes from different sources and drops them into the repo so they can be shown in the README (or elsewhere). Below is how we work together.

---

## TL;DR

* **Have an idea or request? → Open an *Issue*.**
  Use issues to propose new features, discuss improvements, or ask questions.
* **Fixed a bug or added a new source? → Open a *Pull Request (PR)*.**
  PRs are for concrete changes to code, docs, or configuration.

---

## Ground rules

* Be kind and constructive. Assume positive intent.
* Keep PRs focused: one logical change per PR.
* Prefer discussion in a linked Issue if your change is large or controversial.
* By contributing, you agree your contributions will be licensed under this repository’s license.

---

## Getting started (local dev)

1. **Fork** the repo and **clone** your fork.
2. Create and activate a Python virtual environment.
3. Install dependencies (see the project’s requirements file).
4. Run the project locally to verify your changes.

> If the project uses linting/pre-commit hooks, please run them locally before committing (e.g., `pre-commit run --all-files`).

---

## Issues: proposing ideas & reporting problems

Use **Issues** to:

* Propose new features or enhancements
* Suggest new meme **sources** to support
* Report bugs

**When opening an Issue, please include:**

* A clear title and short description
* Steps to reproduce (for bugs)
* Example links or data (for new sources)
* Any screenshots/logs if relevant

**Labels** help triage—use any that fit (e.g., `bug`, `enhancement`).

---

## Pull Requests: fixes & new sources

Open a **PR** when you:

* Fix a bug
* Improve docs or developer experience
* Add a **new source** (see the guide below)

**PR checklist**

* [ ] The change is scoped and clear
* [ ] Code is formatted and linted; tests added/updated if applicable
* [ ] README/Docs updated if behavior or configuration changed
* [ ] Screenshots or sample output included if it helps review

**PR style**

* Reference related Issues with `Fixes #123` or `Closes #123` where relevant.
* Prefer meaningful commit messages (e.g., Conventional Commit style is welcome but not required).
* Keep diffs small; split large changes into multiple PRs.

---

## Adding a new source (high level guide)

> The exact structure may vary; follow existing patterns in the `sources/` directory.

1. **Create a new module** for your source (e.g., `sources/<your_source>.py`).
2. **Follow the existing interface** used by current sources (look at other source files for the expected class/functions and return types).
3. **Handle media types** the project supports (images/GIFs). If your source could return other media, convert or filter appropriately.
4. **Add your source to the registry/config** so the main runner includes it.
5. **Test locally** to ensure files are generated to the expected `memes/<source>/...` paths.
6. **Document** any configuration (API keys, env vars) needed for your source in the README or in your PR description.

> Tip: If your new source requires credentials or rate limits, add sensible error handling and clear messages for contributors.

---

## Development notes

* Prefer small, readable functions and explicit error messages.
* Log enough detail to debug failures in CI and local runs.
* Don’t commit secrets. Use environment variables and `.env` locally if needed (but do **not** commit `.env`).

---

## Code of Conduct

We follow a simple rule: be respectful and inclusive. Harassment or discrimination of any kind is not tolerated. If there’s a problem, open an Issue or contact a maintainer.

---

## Release & CI

* CI will run on PRs. Make sure the basic fetch flow works and that generated files are correctly ignored/committed as intended.
* If your change affects the scheduled workflow (cron), mention it in the PR description so maintainers can double‑check timing and permissions.

---

## Questions?

* Open an Issue with the `question` label.
* Or start a draft PR early to get feedback on direction.

Thanks again for contributing! 🙌
