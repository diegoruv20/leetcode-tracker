from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def dashboard():
    return render_template("dashboard.html")


@views_bp.route("/problems")
def problems():
    return render_template("problems.html")


@views_bp.route("/problems/<int:problem_id>")
def problem_detail(problem_id):
    return render_template("detail.html", problem_id=problem_id)


@views_bp.route("/log")
def log_attempt():
    return render_template("log.html")
