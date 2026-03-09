# Flask Task Tracker

Task tracking web app built with Flask + SQLAlchemy, including authentication and pending/done task flows.

## Features

- User registration and login with hashed passwords
- Session-based authentication
- Add, update, complete, and delete tasks
- Separate pending and completed pages
- Health check route: `/healthz`

## Tech Stack

- Python 3.x
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- PostgreSQL (Neon) or SQLite (local fallback)
- Gunicorn for production serving

## Project Structure

```text
Flask-Task_Tracker/
|-- app.py
|-- requirements.txt
|-- start.sh
|-- .env.example
|-- static/
|-- templates/
`-- instance/
```

## Local Development

1. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Set environment variables (PowerShell example)

```powershell
$env:FLASK_ENV="development"
$env:FLASK_DEBUG="1"
$env:SECRET_KEY="dev-secret"
$env:DATABASE_URL="sqlite:///tasks.db"
```

4. Run app

```powershell
python app.py
```

App runs at `http://127.0.0.1:5000`.

## Deployment (Neon + Gunicorn)

Set these required environment variables in your hosting platform:

- `SECRET_KEY` (required in production)
- `DATABASE_URL` (your Neon PostgreSQL connection string)
- `FLASK_ENV=production`
- `PORT` (provided by most platforms automatically)

Optional Gunicorn tuning:

- `GUNICORN_WORKERS` (default `2`)
- `GUNICORN_THREADS` (default `4`)
- `GUNICORN_TIMEOUT` (default `120`)

Start command:

```bash
bash start.sh
```

or directly:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

## Important Notes

- Never commit real credentials; use environment variables.
- Database tables are created at startup.
- `SECRET_KEY` is enforced for production.
