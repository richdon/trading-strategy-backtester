from extensions import db, bcrypt_instance
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
        self.password_hash = bcrypt_instance.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """
        Verify user password
        """
        return bcrypt_instance.check_password_hash(self.password_hash, password)

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


class LiveTradingStrategy(db.Model):
    """
    SQLAlchemy model for live trading strategy configuration and status
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    backtest_id = db.Column(db.String(36), db.ForeignKey('backtest_strategy.id'), nullable=False)

    # Strategy configuration
    strategy = db.Column(db.String(50), nullable=False)
    asset = db.Column(db.String(20), nullable=False)
    interval = db.Column(db.String, nullable=False)
    initial_capital = db.Column(db.Float, default=10000)
    strategy_params = db.Column(db.JSON, default=dict)

    # Strategy status
    is_active = db.Column(db.Boolean, default=True)
    last_check_time = db.Column(db.DateTime)
    last_signal_time = db.Column(db.DateTime)
    error_count = db.Column(db.Integer, default=0)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('live_strategies', lazy=True))
    backtest = db.relationship('BacktestStrategy', backref=db.backref('live_strategies', lazy=True))

    def __repr__(self):
        return f'<LiveTradingStrategy {self.strategy} - {self.asset} - {self.interval}>'

    def to_dict(self):
        """
        Convert strategy to dictionary for serialization
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'backtest_id': self.backtest_id,
            'strategy': self.strategy,
            'asset': self.asset,
            'interval': self.interval,
            'initial_capital': self.initial_capital,
            'strategy_params': self.strategy_params,
            'is_active': self.is_active,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'last_signal_time': self.last_signal_time.isoformat() if self.last_signal_time else None,
            'error_count': self.error_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
