from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Flask app and database setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key") #
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///tasks.db"  # fallback for local dev
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
        )


    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title} - {self.desc} - {self.date_created}"

# ROUTES
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

    allTasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", allTasks=allTasks)

# Route for task update
@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    task = Task.query.filter_by(sno=sno).first()
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]

        task = Task.query.filter_by(sno=sno).first()
        task.title = title
        task.desc = desc
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    return render_template("update.html", task=task)

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
    app.run(debug=True)
