from extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
import uuid


class User(UserMixin, db.Model):
    """
    User model for authentication and profile management
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationship with BacktestStrategy
    backtests = db.relationship('BacktestStrategy', backref='user', lazy=True)

    def set_password(self, password):
        """
        Hash and set user password
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """
        Verify user password
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        Convert user to dictionary for serialization
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


class BacktestStrategy(db.Model):
    """
    SQLAlchemy model to store backtest configurations and results
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to link backtest with user
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    asset = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    interval = db.Column(db.String, nullable=False)
    initial_capital = db.Column(db.Float, default=10000)

    # JSON column for flexible strategy parameters
    strategy_params = db.Column(db.JSON, default=dict)

    # Store backtest results
    backtest_results = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BacktestStrategy {self.strategy} - {self.asset} - {self.interval}>'
