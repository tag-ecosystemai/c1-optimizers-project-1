"""Application factory for the Customer Intelligence Classifier frontend."""

import os

from flask import Flask, flash, redirect, url_for
from werkzeug.exceptions import RequestEntityTooLarge


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret-key-change-me")
    # Matches the "200MB per file" limit shown on the bulk upload screen.
    app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

    from .blueprints.main import bp as main_bp

    app.register_blueprint(main_bp)

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(_error):
        flash("That file is larger than the 200MB limit. Choose a smaller CSV.", "error")
        return redirect(url_for("main.bulk_upload"))

    return app
