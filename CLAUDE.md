# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Spendly**: a Flask personal expense tracker (amounts in ₹). It's a CampusX course project built step by step: `app.py` and `database/db.py` contain placeholders marked "coming in Step N" / "Students will write this file in Step 1", which are filled in as the course progresses. Keep that step structure intact when implementing a step, and don't build later steps ahead of time unless asked.

## Environment (Windows + Git Bash)

- The virtualenv is `venv/` and its executables live in `venv/Scripts/` (Windows layout), **not** `venv/bin/`.
- Each shell command starts a fresh shell, so `source venv/Scripts/activate` doesn't persist. A SessionStart hook in `.claude/settings.local.json` puts `venv/Scripts` first on PATH. If `python`/`python3` ever resolves to the system Python (`ModuleNotFoundError: No module named 'flask'`), call `venv/Scripts/python` explicitly.
- Don't re-source `activate` inside this session: the parent terminal may already have a Windows-format venv PATH, and `activate`'s `deactivate` step restores it and breaks bash's PATH.

## Commands

```bash
venv/Scripts/python -m pip install -r requirements.txt   # install deps
venv/Scripts/python app.py                               # run dev server → http://127.0.0.1:5001 (debug + auto-reload)
venv/Scripts/python -m pytest                            # run tests (pytest + pytest-flask; no tests/ dir yet)
venv/Scripts/python -m pytest tests/test_x.py::test_name # run a single test
```

The server runs on port **5001**, not Flask's default 5000. Before starting it, check whether it's already running (`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/`). There's no linter or build step.

## Architecture

- **`app.py`**: the single Flask app with every route. There are no blueprints and no app factory, so a `pytest-flask` `app` fixture must import `app` from `app.py` directly.
- **`database/db.py`**: the data layer, plain `sqlite3` with no ORM. The planned interface is `get_db()` (connection with `row_factory` set and `PRAGMA foreign_keys` enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS …`) and `seed_db()` (dev sample data). Routes should call these instead of embedding connection logic. The SQLite file `expense_tracker.db` is gitignored.
- **`templates/`**: Jinja templates. Every page `{% extends "base.html" %}` and fills the `title`, `content`, and optional `head`/`scripts` blocks. `base.html` holds the navbar (currently always shows Sign in / Get started, with no auth-aware state yet) and the footer (links to `/terms`, `/privacy`).
- **`static/css/style.css`**: one stylesheet driven by CSS custom properties on `:root` (`--ink*`, `--paper*`, `--accent`, `--danger`, `--font-display` = DM Serif Display, `--font-body` = DM Sans, `--radius-*`). Use these tokens rather than hard-coded colours or fonts. Fonts load from Google Fonts in `base.html`.
- **`static/js/main.js`**: vanilla JS, empty for now. There's no frontend framework or bundler.

### Current gaps to be aware of

- `register.html` and `login.html` submit `POST` to `/register` and `/login`, but those routes are GET-only, so a form submit returns 405 until auth is implemented. The templates already render an `{{ error }}` message if one is passed.
- `/logout`, `/profile`, and `/expenses/add|<id>/edit|<id>/delete` return placeholder strings.
- No `SECRET_KEY` is set yet, and sessions or flash messages need one.
