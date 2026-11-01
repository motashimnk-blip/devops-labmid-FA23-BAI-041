"""Assignment Submission Portal (Flask app)."""
import os

from flask import Flask, redirect, render_template, request, url_for

from portal import storage
from portal.validation import validate_submission


def create_app(db_path=None):
    app = Flask(__name__, template_folder="../templates")
    app.config["DB_PATH"] = db_path or os.environ.get("PORTAL_DB", "submissions.db")
    storage.init_db(app.config["DB_PATH"])

    @app.route("/", methods=["GET"])
    def index():
        submissions = storage.list_submissions(app.config["DB_PATH"])
        return render_template("index.html", submissions=submissions,
                               errors=[], form={}, saved=request.args.get("saved"))

    @app.route("/submit", methods=["POST"])
    def submit():
        form = {
            "name": request.form.get("name", "").strip(),
            "reg_no": request.form.get("reg_no", "").strip(),
            "title": request.form.get("title", "").strip(),
            "url": request.form.get("url", "").strip(),
        }
        errors = validate_submission(form)
        if errors:
            submissions = storage.list_submissions(app.config["DB_PATH"])
            return render_template("index.html", submissions=submissions,
                                   errors=errors, form=form, saved=None), 400

        storage.add_submission(app.config["DB_PATH"], form)
        return redirect(url_for("index", saved=1))

    return app
