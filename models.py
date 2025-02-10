from extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy import Index, text


class User(UserMixin, db.Model):
    """
    User model for authentication and profile management
    """
    __tablename__ = 'users'

    # Use PostgreSQL native UUID type
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=text('now()'))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    # Add indexes for frequently queried fields
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
    )

    # Relationship with BacktestStrategy
    backtests = db.relationship('BacktestStrategy', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify user password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary for serialization"""
        return {
            'id': str(self.id),  # Convert UUID to string
            'username': self.username,
            'email': self.email
        }


class BacktestStrategy(db.Model):
    """
    SQLAlchemy model to store backtest configurations and results
    """
    __tablename__ = 'backtest_strategies'

    # Use PostgreSQL native UUID type
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    strategy = db.Column(db.String(50), nullable=False)
    asset = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    interval = db.Column(db.String(10), nullable=False)
    initial_capital = db.Column(db.Numeric(20, 8), default=10000)  # Using Numeric for precise financial calculations

    # Use PostgreSQL's native JSON type
    strategy_params = db.Column(JSON, default=dict)
    backtest_results = db.Column(JSON)

    created_at = db.Column(db.DateTime(timezone=True), server_default=text('now()'))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_backtest_user_id_created', user_id, created_at.desc()),
        Index('idx_backtest_strategy_asset', strategy, asset),
        Index('idx_backtest_date_range', start_date, end_date),
    )

    def __repr__(self):
        return f'<BacktestStrategy {self.strategy} - {self.asset} - {self.interval}>'

    def to_dict(self):
        """Convert backtest to dictionary for serialization"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'strategy': self.strategy,
            'asset': self.asset,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'interval': self.interval,
            'initial_capital': float(self.initial_capital),  # Convert Decimal to float for JSON serialization
            'strategy_params': self.strategy_params,
            'backtest_results': self.backtest_results,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
