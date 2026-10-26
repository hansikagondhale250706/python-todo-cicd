import os
import sqlite3

from flask import Flask, redirect, render_template, request, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "tasks.db")
    )

    if test_config:
        app.config.update(test_config)

    def get_db():
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        return connection

    def init_db():
        with get_db() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        with get_db() as connection:
            tasks = connection.execute(
                "SELECT * FROM tasks ORDER BY id DESC"
            ).fetchall()

        return render_template("index.html", tasks=tasks)

    @app.route("/add", methods=["POST"])
    def add_task():
        title = request.form.get("title", "").strip()

        if title:
            with get_db() as connection:
                connection.execute(
                    "INSERT INTO tasks (title) VALUES (?)",
                    (title,)
                )

        return redirect(url_for("index"))

    @app.route("/complete/<int:task_id>", methods=["POST"])
    def complete_task(task_id):
        with get_db() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET completed = CASE completed
                    WHEN 0 THEN 1 ELSE 0
                END
                WHERE id = ?
                """,
                (task_id,)
            )

        return redirect(url_for("index"))

    @app.route("/delete/<int:task_id>", methods=["POST"])
    def delete_task(task_id):
        with get_db() as connection:
            connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,)
            )

        return redirect(url_for("index"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)