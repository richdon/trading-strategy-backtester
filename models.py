from extensions import db
from datetime import datetime
import uuid


class BacktestStrategy(db.Model):
    """
    SQLAlchemy model to store backtest configurations and results
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Strategy Configuration
    STRATEGY_CHOICES = [
        'MACD Crossover',
        'Simple Moving Average'
    ]

    ASSET_CHOICES = [
        'BTC/USDT',
        'ETH/USDT'
    ]

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
