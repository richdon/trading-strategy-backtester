import pandas as pd
import numpy as np
import yfinance as yf
from typing import Any


class TradingStrategies:
    @staticmethod
    def mac_d_crossover_params_by_interval(interval: str):
        return {
            "1m": {
                "fast_period": 5,
                "slow_period": 15,
                "signal_period": 5
            },
            "5m": {
                "fast_period": 6,
                "slow_period": 20,
                "signal_period": 7
            },
            "15m": {
                "fast_period": 8,
                "slow_period": 24,
                "signal_period": 9
            },
            "1h": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9
            },
            "4h": {
                "fast_period": 15,
                "slow_period": 40,
                "signal_period": 10
            },
            "1d": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9  # Default daily MACD values
            },
            "1w": {
                "fast_period": 20,
                "slow_period": 50,
                "signal_period": 10
            }
        }.get(interval, {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        })

    @staticmethod
    def moving_average_params_by_interval(interval: str):
        return {
            "1m": {
                "short_period": 5,
                "long_period": 15
            },
            "5m": {
                "short_period": 8,
                "long_period": 20
            },
            "15m": {
                "short_period": 10,
                "long_period": 30
            },
            "1h": {
                "short_period": 20,
                "long_period": 50
            },
            "4h": {
                "short_period": 50,
                "long_period": 200
            },
            "1d": {
                "short_period": 50,
                "long_period": 200  # Default daily MA crossover values
            },
            "1w": {
                "short_period": 10,
                "long_period": 50
            }
        }.get(interval, {
            "short_period": 50,
            "long_period": 200
        })

    @staticmethod
    def fetch_price_data(
            asset: str,
            start_date: str,
            end_date: str,
            interval: str
    ) -> pd.DataFrame:
        """
        Fetch historical price data with flexible interval support

        Supported intervals:
        - '1m': 1 minute
        - '2m': 2 minutes
        - '5m': 5 minutes
        - '15m': 15 minutes
        - '30m': 30 minutes
        - '1h': 1 hour
        - '1d': 1 day
        - '1wk': 1 week
        - '1mo': 1 month
        """
        # Validate interval
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval. Choose from {valid_intervals}")

        try:
            # Convert asset to yfinance format
            ticker = asset.replace('/', '-')

            # Fetch data with specified interval
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval=interval
            )

            # Add additional calculated columns
            data['Returns'] = data['Close'].pct_change()
            data['Log_Returns'] = np.log(1 + data['Returns'])

            return data

        except Exception as e:
            raise ValueError(f"Error fetching data: {str(e)}")

    @classmethod
    def macd_crossover_strategy(
            cls,
            data: pd.DataFrame,
            initial_capital: float,
            interval: str,
            params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        MACD Crossover Strategy with Interval and Parameter Flexibility
        """

        # Default or custom MACD parameters
        fast_period = params['fast_period']
        slow_period = params['slow_period']
        signal_period = params['signal_period']

        # Calculate MACD
        exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()

        # Trading simulation
        position = 0
        capital = initial_capital
        trades = []

        # Interval-based multipliers for position sizing and risk management
        interval_multipliers = {
            '1m': 0.1,  # Very conservative for minute-level trading
            '5m': 0.2,  # Slightly more aggressive
            '15m': 0.3,  # Moderate aggression
            '1h': 0.5,  # More substantial position sizing
            '1d': 1.0  # Full position for daily intervals
        }
        position_multiplier = interval_multipliers.get(interval, 0.5)

        for i in range(len(data)):
            trade = "HOLD"
            close_price = data['Close'][i]
            if i < slow_period:
                trades.append({
                    'date': data.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                    'portfolio_value': capital,
                    'position': position,
                    'price': close_price,
                    'capital': capital,
                    'asset': close_price * position,
                    'trade': trade
                })
                continue

            # Advanced trading signals with interval considerations
            buy_signal = (
                    macd[i] > signal[i] and
                    macd[i - 1] <= signal[i - 1]
            )

            sell_signal = (
                    macd[i] < signal[i] and
                    macd[i - 1] >= signal[i - 1]
            )

            if buy_signal:
                # Dynamic position sizing based on interval
                investment_amount = capital * position_multiplier
                shares_to_buy = investment_amount / close_price
                position += shares_to_buy
                capital -= investment_amount
                trade = "BUY"

            elif sell_signal:
                # Partial or full position liquidation
                sell_portion = position * position_multiplier
                capital += sell_portion * close_price
                position -= sell_portion
                trade = "SELL"

            asset = position * close_price
            trades.append({
                'date': data.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                'portfolio_value': capital + asset,
                'position': position,
                'price': close_price,
                'capital': capital,
                'asset': asset,
                'trade': trade
            })

        # Calculate performance metrics
        final_portfolio_value = capital + (position * data['Close'].iloc[-1])
        total_return = ((final_portfolio_value / initial_capital) - 1) * 100

        # Volatility and risk metrics
        returns = data['Returns'].dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # Annualized

        return {
            'trades': trades,
            'final_portfolio_value': final_portfolio_value,
            'total_return_percentage': total_return,
            'sharpe_ratio': sharpe_ratio,
            'interval': interval,
            'initial_capital': initial_capital
        }

    @classmethod
    def moving_average_strategy(
            cls,
            data: pd.DataFrame,
            initial_capital: float,
            interval: str,
            params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Moving Average Strategy with Interval Support
        """
        # Configurable moving average parameters
        short_window = params.get('short_period', 20)
        long_window = params.get('long_period', 50)

        # Calculate moving averages
        data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
        data['Long_MA'] = data['Close'].rolling(window=long_window).mean()

        # Interval-based position sizing
        interval_multipliers = {
            '1m': 0.1,
            '5m': 0.2,
            '15m': 0.3,
            '1h': 0.5,
            '1d': 1.0
        }
        position_multiplier = interval_multipliers.get(interval, 0.5)

        # Trading simulation
        position = 0
        capital = initial_capital
        trades = []

        for i in range(len(data)):
            trade = 'HOLD'
            close_price = data['Close'][i]
            if i < long_window:
                trades.append({
                    'date': data.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                    'portfolio_value': capital,
                    'position': position,
                    'price': close_price,
                    'capital': capital,
                    'asset': close_price * position,
                    'trade': trade
                })
                continue

            # Crossover trading signals
            buy_signal = (
                    data['Short_MA'][i] > data['Long_MA'][i] and
                    data['Short_MA'][i - 1] <= data['Long_MA'][i - 1]
            )

            sell_signal = (
                    data['Short_MA'][i] < data['Long_MA'][i] and
                    data['Short_MA'][i - 1] >= data['Long_MA'][i - 1]
            )

            if buy_signal:
                # Dynamic position sizing
                investment_amount = capital * position_multiplier
                shares_to_buy = investment_amount / close_price
                position += shares_to_buy
                capital -= investment_amount
                trade = 'BUY'

            elif sell_signal:
                # Partial or full position liquidation
                sell_portion = position * position_multiplier
                capital += sell_portion * close_price
                position -= sell_portion
                trade = 'SELL'

            asset = position * close_price
            trades.append({
                'date': data.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                'portfolio_value': capital + (position * close_price),
                'position': position,
                'price': close_price,
                'capital': capital,
                'asset': asset,
                'trade': trade
            })

        # Performance metrics
        final_portfolio_value = capital + (position * data['Close'].iloc[-1])
        total_return = ((final_portfolio_value / initial_capital) - 1) * 100

        # Volatility and risk metrics
        returns = data['Returns'].dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # Annualized

        return {
            'trades': trades,
            'final_portfolio_value': final_portfolio_value,
            'total_return_percentage': total_return,
            'sharpe_ratio': sharpe_ratio,
            'interval': interval,
            'initial_capital': initial_capital
        }


# Example usage in views or testing
def run_backtest_example():
    """
    Example of how to use the strategies with interval support
    """
    # Example configuration
    backtest_params = {
        'asset': 'BTC/USDT',
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'strategy_params': {
            'interval': '1h',  # 1-hour interval
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        },
        'initial_capital': 10000
    }

    # Fetch data
    price_data = TradingStrategies.fetch_price_data(
        backtest_params['asset'],
        backtest_params['start_date'],
        backtest_params['end_date'],
        backtest_params['strategy_params']['interval']
    )

    # Run backtest
    results = TradingStrategies.macd_crossover_strategy(
        price_data,
        backtest_params['strategy_params'],
        backtest_params['initial_capital']
    )

    return results
