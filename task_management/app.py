from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from models import User, Task
        db.create_all()

    from routes import auth_bp, task_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
