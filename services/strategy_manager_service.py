from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Dict, Optional
from models import LiveTradingStrategy, User
from extensions import db


@dataclass
class StrategyStatus:
    """Data class to hold strategy status information"""
    strategy_id: str
    user_id: str
    last_check: datetime
    last_signal: datetime
    error_count: int
    is_active: bool


class StrategyManager:
    def __init__(self, email_service=None):
        self.strategy_statuses: Dict[str, StrategyStatus] = {}
        self.email_service = email_service
        self.logger = logging.getLogger(__name__)

    def add_strategy(self, strategy_id: str, user_id: str) -> None:
        """Add a new strategy to monitor"""
        self.strategy_statuses[strategy_id] = StrategyStatus(
            strategy_id=strategy_id,
            user_id=user_id,
            last_check=datetime.utcnow(),
            last_signal=datetime.min,
            error_count=0,
            is_active=True
        )

    def get_strategy_status(self, strategy_id: str) -> Optional[StrategyStatus]:
        """Get the current status of a strategy"""
        return self.strategy_statuses.get(strategy_id)

    def update_status(self, strategy_id: str, had_error: bool = False) -> None:
        """Update strategy status after a check"""
        if strategy_id in self.strategy_statuses:
            status = self.strategy_statuses[strategy_id]
            status.last_check = datetime.utcnow()

            if had_error:
                status.error_count += 1
                if status.error_count >= 5:  # Disable after 5 consecutive errors
                    self._disable_strategy(strategy_id)
            else:
                status.error_count = 0

            # Update database record
            try:
                strategy = LiveTradingStrategy.query.get(strategy_id)
                if strategy:
                    strategy.last_check_time = status.last_check
                    strategy.error_count = status.error_count
                    db.session.commit()
            except Exception as e:
                self.logger.error(f"Error updating strategy status in database: {str(e)}")

    def record_signal(self, strategy_id: str) -> None:
        """Record when a signal was generated"""
        if strategy_id in self.strategy_statuses:
            status = self.strategy_statuses[strategy_id]
            status.last_signal = datetime.utcnow()

            try:
                strategy = LiveTradingStrategy.query.get(strategy_id)
                if strategy:
                    strategy.last_signal_time = status.last_signal
                    db.session.commit()
            except Exception as e:
                self.logger.error(f"Error updating signal time in database: {str(e)}")

    def _disable_strategy(self, strategy_id: str) -> None:
        """Disable a strategy due to errors"""
        try:
            strategy = LiveTradingStrategy.query.get(strategy_id)
            if strategy:
                strategy.is_active = False
                self.strategy_statuses[strategy_id].is_active = False
                db.session.commit()
        except Exception as e:
            self.logger.error(f"Error disabling strategy {strategy_id}: {str(e)}")
