import os
from sqlalchemy import inspect, text
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Flask app and database setup
app = Flask(__name__)

ENV = os.environ.get("FLASK_ENV", "development").lower()
IS_PRODUCTION = ENV == "production"

secret_key = os.environ.get("SECRET_KEY")
if IS_PRODUCTION and not secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required in production.")
app.secret_key = secret_key or "dev-secret-key"

database_url = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
# Some platforms still provide postgres:// URLs.
database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = IS_PRODUCTION
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
db = SQLAlchemy(app)



# MODELS
# Authentication model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Database model
class Task(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title} - {self.desc} - {self.date_created}"


# Ensure tables exist before handling requests (helps avoid 500s on auth routes)
with app.app_context():
    db.create_all()
    # Add new columns to existing SQLite DBs created before this field existed.
    columns = {column["name"] for column in inspect(db.engine).get_columns("task")}
    if "completed" not in columns:
        db.session.execute(
            text("ALTER TABLE task ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 0")
        )
        db.session.commit()


# ROUTES
# Health check route for load balancers and uptime checks.
@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            error = "User already exists"
        else:
            user = User(username=username)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()
            return redirect("/login")

    return render_template("register.html", error=error)


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user is None:
            return redirect("/register")

        if not user.check_password(password):
            return "Invalid credentials", 401

        session["user_id"] = user.id
        return redirect("/")

    return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


# Route for task addition and display
@app.route("/", methods=["GET", "POST"])
def home():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]

        task = Task(title=title, desc=desc, user_id=session["user_id"])
        db.session.add(task)
        db.session.commit()
        return redirect("/")

    allTasks = Task.query.filter_by(user_id=session["user_id"], completed=False).all()
    return render_template("index.html", allTasks=allTasks)


# Route for completed tasks display
@app.route("/done")
def done():
    if "user_id" not in session:
        return redirect("/login")

    done_tasks = Task.query.filter_by(user_id=session["user_id"], completed=True).all()
    return render_template("done.html", done_tasks=done_tasks)


# Route for pending tasks display
@app.route("/pending")
def pending():
    if "user_id" not in session:
        return redirect("/login")

    pending_tasks = Task.query.filter_by(
        user_id=session["user_id"], completed=False
    ).all()
    return render_template("pending.html", pending_tasks=pending_tasks)


# Route for task update
@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    if "user_id" not in session:
        return redirect("/login")

    task = Task.query.filter_by(sno=sno, user_id=session["user_id"]).first()
    if task is None:
        return "Task not found", 404

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]

        task.title = title
        task.desc = desc
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    return render_template("update.html", task=task)


# Route for marking task as completed
@app.route("/complete/<int:sno>", methods=["POST"])
def complete(sno):
    if "user_id" not in session:
        return redirect("/login")

    task = Task.query.filter_by(sno=sno, user_id=session["user_id"]).first()
    if task is None:
        return "Task not found", 404

    task.completed = True
    db.session.commit()
    return redirect("/")


# Route for task deletion
@app.route("/delete/<int:sno>", methods=["POST"])
def delete(sno):
    task = Task.query.filter_by(sno=sno, user_id=session["user_id"]).first()
    if task is None:
        return "Task not found", 404

    db.session.delete(task)
    db.session.commit()
    return redirect("/")


# Run the app
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
