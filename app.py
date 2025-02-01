from database_utils import init_db_commands
from extensions import db, login_manager, ma, bcrypt, jwt
from flask import Flask

from models import User
from routes import initialize_routes, register_routes, configure_swagger_ui
from auth import auth_ns
from backtest import backtest_ns


def create_app():
    app = Flask(__name__)

    # Initialize Swagger routes
    blueprint, api = initialize_routes()

    # Register routes with the application
    register_routes(app, blueprint)

    # Configure Swagger UI
    configure_swagger_ui(app)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backtest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure random key
    app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'  # Replace with a secure random key

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
