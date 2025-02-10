import os
from database_utils import init_db_commands
from extensions import db, login_manager, ma, bcrypt, jwt
from flask import Flask

from models import User
from routes import initialize_routes, register_routes, configure_swagger_ui
from auth import auth_ns
from backtest import backtest_ns
from dotenv import load_dotenv
from config import config

load_dotenv()


def create_app(config_name: str = None):
    app = Flask(__name__)

    # Use environment variable if config_name not provided
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Load the configuration
    app.config.from_object(config[config_name])

    # Initialize Swagger routes
    blueprint, api = initialize_routes()

    # Register routes with the application
    register_routes(app, blueprint)

    # Configure Swagger UI
    configure_swagger_ui(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Add CLI commands
    init_db_commands(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Add namespaces
    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(backtest_ns, path='/api/backtest')

    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database initialization error (this is often okay on startup): {e}")

    return app


# Create the application instance
app = create_app()

if __name__ == '__main__':
    # app = create_app()
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
