from flask import Flask
from database_utils import init_db_commands
from extensions import db, login_manager, ma, bcrypt, jwt
from auth import auth_bp
from controller import backtest_bp
from models import User


def create_app():
    app = Flask(__name__)

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

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(backtest_bp, url_prefix='/api')

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
