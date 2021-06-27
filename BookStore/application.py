from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('BookStore.config.Config')
    # app.config['SQLALCHEMY_ECHO'] = False
    # Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Include our Routes
        import BookStore.api
        # Register Blueprints
        app.register_blueprint(BookStore.api.book_store)

    return app
