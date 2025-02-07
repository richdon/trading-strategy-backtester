import threading
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from models import LiveTradingStrategy, User
from services.rate_limiter_service import RateLimiter
from services.strategy_manager_service import StrategyManager


class TradingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TradingService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.rate_limiter = RateLimiter()
        self.strategy_manager = StrategyManager()
        self.logger = logging.getLogger(__name__)
        self._initialized = True

    def check_signals(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        try:
            strategy = LiveTradingStrategy.query.get(strategy_id)
            if not strategy or not strategy.is_active:
                return None

            user = User.query.get(strategy.user_id)

            # Fetch latest market data
            ticker = strategy.asset.replace('/', '-')
            data = yf.download(
                ticker,
                period='1d',
                interval=strategy.interval
            )

            if data.empty:
                return None

            # Run strategy analysis
            if strategy.strategy == 'MACD Crossover':
                signal = self._check_macd_strategy(data, strategy)
            else:
                signal = self._check_ma_strategy(data, strategy)

            # Update strategy status
            self.strategy_manager.update_status(strategy_id, had_error=False)

            if signal and signal['trade'] in ['BUY', 'SELL']:
                # Record signal
                self.strategy_manager.record_signal(strategy_id)

                return {
                    'strategy_id': strategy_id,
                    'signal_type': signal['trade'],
                    'price': signal['price'],
                    'amount': signal['position'],
                    'timestamp': datetime.utcnow()
                }

            return None

        except Exception as e:
            self.logger.error(f"Error checking signals for strategy {strategy_id}: {str(e)}")
            self.strategy_manager.update_status(strategy_id, had_error=True)
            return None

    @staticmethod
    def _check_macd_strategy(data: pd.DataFrame, strategy: LiveTradingStrategy) -> dict[str, Any]:
        """
        Check for MACD signals
        """
        params = strategy.strategy_params
        fast_period = params.get('fast_period', 12)
        slow_period = params.get('slow_period', 26)
        signal_period = params.get('signal_period', 9)

        # Calculate MACD
        exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()

        # Get latest values
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        prev_macd = macd.iloc[-2]
        prev_signal = signal.iloc[-2]

        # Check for crossovers
        if current_macd > current_signal and prev_macd <= prev_signal:
            return {
                'trade': 'BUY',
                'price': data['Close'].iloc[-1],
                'position': 1.0  # Position size calculation could be more sophisticated
            }
        elif current_macd < current_signal and prev_macd >= prev_signal:
            return {
                'trade': 'SELL',
                'price': data['Close'].iloc[-1],
                'position': 1.0
            }

        return {'trade': 'HOLD', 'price': data['Close'].iloc[-1], 'position': 0}

    @staticmethod
    def _check_ma_strategy(data: pd.DataFrame, strategy: LiveTradingStrategy) -> dict[str, Any]:
        """
        Check for Moving Average signals
        """
        params = strategy.strategy_params
        short_period = params.get('short_period', 50)
        long_period = params.get('long_period', 200)

        # Calculate moving averages
        short_ma = data['Close'].rolling(window=short_period).mean()
        long_ma = data['Close'].rolling(window=long_period).mean()

        # Get latest values
        current_short = short_ma.iloc[-1]
        current_long = long_ma.iloc[-1]
        prev_short = short_ma.iloc[-2]
        prev_long = long_ma.iloc[-2]

        # Check for crossovers
        if current_short > current_long and prev_short <= prev_long:
            return {
                'trade': 'BUY',
                'price': data['Close'].iloc[-1],
                'position': 1.0
            }
        elif current_short < current_long and prev_short >= prev_long:
            return {
                'trade': 'SELL',
                'price': data['Close'].iloc[-1],
                'position': 1.0
            }

        return {'trade': 'HOLD', 'price': data['Close'].iloc[-1], 'position': 0}
