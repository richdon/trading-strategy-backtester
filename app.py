import os

from database_utils import init_db_commands
from extensions import db, login_manager, ma, jwt, bcrypt_instance
from flask import Flask
from flask_mail import Mail

from models import User
from routes import initialize_routes, register_routes, configure_swagger_ui
from auth import auth_ns
from backtest import backtest_ns
from live_trading import live_trading_ns
from services.email_service import EmailService
from services.trading_service import TradingService
from services.scheduler_service import TradingScheduler

mail = Mail()
email_service = EmailService(mail)
trading_service = TradingService()
trading_scheduler = TradingScheduler()


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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Replace with a secure random key

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    ma.init_app(app)
    bcrypt_instance.init_app(app)
    jwt.init_app(app)

    # Add CLI commands
    init_db_commands(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'

    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # Initialize trading scheduler with trading service
    trading_scheduler.init_app(app, trading_service)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Add namespaces
    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(backtest_ns, path='/api/backtest')
    api.add_namespace(live_trading_ns, path='/api/live')

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
