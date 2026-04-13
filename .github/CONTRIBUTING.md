<!-- SPDX-FileCopyrightText: 2026 Bora Yarkın -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

# Contributing

Thanks for helping improve Dev-Blog.

## Before you start

- Check existing issues and pull requests to avoid duplicate work.
- Open an issue first for large changes, design shifts, or breaking behavior.
- Read the [Code of Conduct](./CODE_OF_CONDUCT.md) before participating.

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the app with `python app.py`.
4. Open `http://localhost:5000/setup` to initialize local content if needed.

## Development guidelines

- Keep changes focused and easy to review.
- Update docs when behavior, setup, or configuration changes.
- Add or update SPDX notices on new tracked files.
- Prefer keeping project meta files in `.github/` unless a root-level file is conventional.
- Update `CHANGELOG.md` for user-visible changes.

## Validation

Before opening a pull request, run what applies locally:

- `python -m compileall app.py tools`
- Manual smoke checks for the setup flow, admin UI, and public pages

## Pull requests

- Use a clear title and explain the problem being solved.
- Link related issues when relevant.
- Include screenshots or short notes for UI changes.
- Call out follow-up work or known limitations.

## Licensing

By contributing to this repository, you agree that your contributions will be
licensed under GNU GPL v3 only (`GPL-3.0-only`).
