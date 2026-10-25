
import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///todo.db"
)

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    task = db.Column(db.String(1000), nullable=False)
    due = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    data = Todo.query.all()

    context = [
        {
            "id": item.id,
            "title": item.title,
            "task": item.task,
            "due": item.due,
        }
        for item in data
    ]

    app.logger.debug("Retrieved %s tasks", len(context))
    return render_template("todo.html", todo=context)


@app.route("/add-task", methods=["GET"])
def add_task():
    return render_template("add_task.html")


@app.route("/submit", methods=["POST"])
def create_user():
    title = request.form["title"]
    task = request.form["task"]
    due = request.form["due"]

    new_task = Todo(title=title, task=task, due=due)

    try:
        db.session.add(new_task)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to create task")
        return jsonify({"message": "An internal error occurred"}), 500

    return redirect(url_for("add_task"))


@app.route("/delete/<int:id>", methods=["GET", "DELETE"])
def delete_user(id):
    task = db.session.get(Todo, id)

    if task is None:
        return jsonify({"message": "task not found"}), 404

    try:
        db.session.delete(task)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to delete task")
        return jsonify({"message": "An internal error occurred"}), 500

    return jsonify({"message": "task deleted successfully"}), 200


@app.route("/update_task/<int:id>", methods=["GET", "POST"])
def update_task(id):
    task = db.get_or_404(Todo, id)

    if request.method == "POST":
        task.title = request.form["title"]
        task.task = request.form["task"]
        task.due = request.form["due"]

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception("Failed to update task")
            return "There is an issue while updating the record", 500

        return redirect(url_for("index"))

    return render_template("update.html", task=task)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
