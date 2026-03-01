# Flask TODO Application

A task management web app built with Flask and SQLAlchemy, now with user authentication and task status flows (Pending and Done).

## Features

- User registration and login with hashed passwords
- Session-based authentication and logout
- Add new tasks
- Update existing tasks
- Delete tasks
- Mark tasks as completed
- Separate views for:
- Pending tasks (`/pending`)
- Completed tasks (`/done`)
- Task timestamps (`date_created`)
- Responsive, modern custom UI
- PRG pattern (POST -> Redirect -> GET) on form submissions

## Tech Stack

### Python and backend framework

- Python 3.x
- Flask `3.1.2`
- Flask-SQLAlchemy `3.1.1`
- SQLAlchemy `2.0.46`
- Werkzeug `3.1.5`
- Jinja2 `3.1.6`
- SQLite (default local database)
- Gunicorn `25.0.2` (optional production server)

### CSS framework and frontend styling

- CSS framework used: **None**
- Styling approach: **Custom vanilla CSS** (`static/css/style.css`)
- Template engine: Jinja2 templates in `templates/`
- Fonts: Google Fonts (`Manrope`, `Space Grotesk`)

## Project Structure

```text
05_Flask/
|-- app.py
|-- requirements.txt
|-- README.md
|-- instance/
|   `-- tasks.db
|-- static/
|   `-- css/
|       `-- style.css
`-- templates/
    |-- base.html
    |-- index.html
    |-- pending.html
    |-- done.html
    |-- update.html
    |-- login.html
    `-- register.html
```

## Setup and Run

1. Create and activate a virtual environment

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Run the app

```powershell
python app.py
```

4. Open in browser

```text
http://127.0.0.1:5000
```

## Main Routes

- `GET, POST /register` - Register user
- `GET, POST /login` - Login user
- `GET /logout` - Logout user
- `GET, POST /` - Add and view pending tasks
- `GET /pending` - Pending tasks page
- `GET /done` - Completed tasks page
- `GET, POST /update/<int:sno>` - Update task
- `POST /complete/<int:sno>` - Mark task completed
- `POST /delete/<int:sno>` - Delete task

## Notes

- Database is created automatically at startup.
- Existing databases are auto-updated to include the `completed` column if missing.
- For production, set a strong `SECRET_KEY` environment variable.
