from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Task(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title} - {self.desc} - {self.date_created}"


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]

        task = Task(title=title, desc=desc)
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    
    allTasks = Task.query.all()
    return render_template("index.html", allTasks=allTasks)

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



@app.route("/delete/<int:sno>")
def delete(sno):
    task = Task.query.filter_by(sno=sno).first()
    if task is None:
        return "Task not found", 404
    
    db.session.delete(task)
    db.session.commit()
    return redirect("/")




if __name__ == "__main__":
    app.run(debug=True)
