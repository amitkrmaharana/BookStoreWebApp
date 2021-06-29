from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

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

    # swagger specific
    swagger_url = '/swagger'
    api_url = '/static/swagger.json'
    swagger_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            'app_name': "Book Store"
        }
    )

    with app.app_context():
        # Include our Routes
        import BookStore.api
        # Register Blueprints
        app.register_blueprint(swagger_blueprint, url_prefix=swagger_url)
        app.register_blueprint(BookStore.api.book_store)

    return app
