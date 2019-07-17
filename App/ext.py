from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def init_ext(app):
    db.init_app(app)
    migrate.init_app(app, db)
    DebugToolbarExtension(app)
    jwt.init_app(app)
