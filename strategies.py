import pandas as pd
import numpy as np
import yfinance as yf


class TradingStrategies:
    @staticmethod
    def fetch_price_data(asset: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical price data for a given asset
        """
        try:
            ticker = asset.replace('/', '-')
            data = yf.download(ticker, start=start_date, end=end_date)
            data['Returns'] = data['Close'].pct_change()
            return data
        except Exception as e:
            raise ValueError(f"Error fetching data: {str(e)}")

    @classmethod
    def macd_crossover_strategy(cls, data: pd.DataFrame, params: dict, initial_capital: float) -> dict:
        """
        MACD Crossover Trading Strategy with configurable parameters
        """
        # Default or custom MACD parameters
        fast_period = params.get('fast_period', 12)
        slow_period = params.get('slow_period', 26)
        signal_period = params.get('signal_period', 9)

        # MACD calculations
        exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()

        # Trading simulation
        position = 0
        capital = initial_capital
        trades = []

        for i in range(len(data)):
            if i == 0:
                trades.append({
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'portfolio_value': capital,
                    'position': position
                })
                continue

            # Configurable trading signals
            buy_signal = macd[i] > signal[i] and macd[i - 1] <= signal[i - 1]
            sell_signal = macd[i] < signal[i] and macd[i - 1] >= signal[i - 1]

            if buy_signal:
                shares_to_buy = capital / data['Close'][i]
                position += shares_to_buy
                capital = 0
            elif sell_signal:
                capital += position * data['Close'][i]
                position = 0

            trades.append({
                'date': data.index[i].strftime('%Y-%m-%d'),
                'portfolio_value': capital + (position * data['Close'][i]),
                'position': position
            })

        return {
            'trades': trades,
            'final_portfolio_value': capital + (position * data['Close'].iloc[-1]),
            'total_return_percentage': ((capital + (position * data['Close'].iloc[-1])) / initial_capital - 1) * 100
        }

    @classmethod
    def moving_average_strategy(cls, data: pd.DataFrame, params: dict, initial_capital: float) -> dict:
        """
        Simple Moving Average Trading Strategy
        """
        # Configurable moving average parameters
        window = params.get('period', 20)
        data['MA'] = data['Close'].rolling(window=window).mean()

        position = 0
        capital = initial_capital
        trades = []

        for i in range(len(data)):
            if i < window:
                trades.append({
                    'date': data.index[i].strftime('%Y-%m-%d'),
                    'portfolio_value': capital,
                    'position': position
                })
                continue

            # Configurable entry/exit conditions
            buy_signal = data['Close'][i] > data['MA'][i] and position == 0
            sell_signal = data['Close'][i] < data['MA'][i] and position > 0

            if buy_signal:
                shares_to_buy = capital / data['Close'][i]
                position += shares_to_buy
                capital = 0
            elif sell_signal:
                capital += position * data['Close'][i]
                position = 0

            trades.append({
                'date': data.index[i].strftime('%Y-%m-%d'),
                'portfolio_value': capital + (position * data['Close'][i]),
                'position': position
            })

        return {
            'trades': trades,
            'final_portfolio_value': capital + (position * data['Close'].iloc[-1]),
            'total_return_percentage': ((capital + (position * data['Close'].iloc[-1])) / initial_capital - 1) * 100
        }
