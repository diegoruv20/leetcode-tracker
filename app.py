from flask import Flask
from models import db
import os


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "tracker.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        from models import Category, Problem, Topic, ProblemTopic, Attempt

        db.create_all()

    from api import api_bp
    from views import views_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
