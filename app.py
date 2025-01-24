from flask import Flask
from extensions import db, ma
from controller import backtest_bp


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backtest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    # Register blueprints
    app.register_blueprint(backtest_bp, url_prefix='/api')

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
