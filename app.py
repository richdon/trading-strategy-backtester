import os
from database_utils import init_db_commands
from extensions import db, login_manager, ma, bcrypt, jwt
from flask import Flask

from models import User
from routes import initialize_routes, register_routes, configure_swagger_ui
from auth import auth_ns
from backtest import backtest_ns
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    load_dotenv()
    # Initialize Swagger routes
    blueprint, api = initialize_routes()

    # Register routes with the application
    register_routes(app, blueprint)

    # Configure Swagger UI
    configure_swagger_ui(app)

    # Database Configuration
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME')

    # PostgreSQL database URL
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

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

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
