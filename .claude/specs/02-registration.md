# Spec: Registration

## Overview
Make the existing sign-up form work. `register.html` already POSTs `name`, `email` and `password` to `/register`, but that route only accepts GET, so submitting the form returns 405. This step makes `/register` accept POST. The route validates the input, rejects duplicate emails, stores the new user with a hashed password in the `users` table, and sends the user to the sign-in page with a success message. Registration is the first feature that writes user data, so it comes before Login/Logout (Step 3), which depends on users existing in the database.

## Depends on
- Step 1: Database Setup. Needs `get_db()`, `init_db()` and the `users` table with its `UNIQUE` email constraint.

## Routes
- `GET /register`: render the registration form (existing). Access: public.
- `POST /register`: validate the form, create the user and redirect to `/login` with a success flash. Access: public.

No other new routes. `/login` stays GET-only and Step 3 will implement it.

## Database changes
No database changes. The `users` table in `database/db.py` already has `name`, `email UNIQUE NOT NULL`, `password_hash` and `created_at`.

Add two helper functions to `database/db.py`. They don't change the schema:
- `get_user_by_email(email)`: return the matching `users` row or `None`.
- `create_user(name, email, password)`: hash the password with `generate_password_hash`, insert the row and return the new user id.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html`: after a validation error, refill the `name` and `email` fields with the submitted values (`value="{{ name or '' }}"`). Never refill the password.
  - `templates/login.html`: render flashed messages (`get_flashed_messages(with_categories=true)`) above the form so "Account created — please sign in" appears after registration.
- **Optional:** add an `.auth-success` class to `static/css/style.css`, styled like `.auth-error` but built only from existing CSS variables (for example `--accent`).

## Files to change
- `app.py`: set `app.secret_key`, import `request`, `redirect`, `url_for` and `flash`, and make `register()` handle both `GET` and `POST`.
- `database/db.py`: add `get_user_by_email()` and `create_user()`.
- `templates/register.html`: keep the submitted `name` and `email` values after an error.
- `templates/login.html`: show flashed messages.
- `static/css/style.css`: add the `.auth-success` style if needed.

## Files to create
- `.claude/specs/02-registration.md` (this file)

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs. Use plain `sqlite3` through `get_db()`.
- Parameterised queries only. Never build SQL with string formatting.
- Hash passwords with werkzeug (`generate_password_hash`). Never store or log plaintext.
- Use CSS variables and never hardcode hex values.
- All templates extend `base.html`.
- Put the database code in `database/db.py` helpers. Don't open connections inside the route.
- Strip whitespace from `name` and `email`, and lowercase `email` before checking and inserting it.
- Validate on the server. All fields are required, the email must contain `@`, and the password must be at least 8 characters (the placeholder already says this). If validation fails, re-render `register.html` with `error` set and status 400.
- Duplicate email: re-render with `error="An account with that email already exists"`. As a fallback, also catch `sqlite3.IntegrityError`.
- After a successful insert, redirect to `url_for('login')` (Post/Redirect/Get) and don't re-render.
- Read `SECRET_KEY` from the environment and fall back to a dev-only default. Don't commit a real secret.
- Don't log the user in or touch the session. Step 3 handles that.
- Leave the other "coming in Step N" placeholders as they are.

## Definition of done
- [ ] `GET /register` still renders the form with status 200.
- [ ] Submitting valid details creates a row in `users`, and `password_hash` is a werkzeug hash, not the plaintext password.
- [ ] A successful submit redirects to `/login`, and the page shows "Account created — please sign in".
- [ ] Registering with `demo@spendly.com` (or `DEMO@Spendly.com `) shows "An account with that email already exists" and creates no new row.
- [ ] Submitting a password shorter than 8 characters shows an error and creates no row.
- [ ] Submitting with an empty name, email or password (with the browser's `required` check bypassed) shows an error and creates no row.
- [ ] After an error, the name and email fields keep their values and the password field is empty.
- [ ] No route returns 405 for `POST /register`.
- [ ] The app starts without errors with `venv/Scripts/python app.py` on port 5001.
