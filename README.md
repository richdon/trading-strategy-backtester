# trading-strategy-backtester

Allows users to backtest test trading stratigies (Simple Moving Average and MACD Crossover), with user defied configurations. Default arguments for strategy parameters are assigned depeneding on the granularity (1m, 5m, 15m, 1h, 1wk) selected by user. 

## Installation and Setup

### Prerequisites

Python 3.11

Pipenv or virtualenv (optional, for dependency management)

### Steps

Clone the repository:
```
git clone https://github.com/richdon/trading-strategy-backtester.git
cd trading-backtesting-bot
```

Create and activate a virtual environment (optional):
```
python -m venv venv
source venv/bin/activate # For Linux/Mac
venv\Scripts\activate   # For Windows
```
Install dependencies:

`pip install -r requirements.txt`

Start the Flask development server:

`flask run`

The app will be accessible at http://127.0.0.1:5000/.


### Test input for `/api/backtest`
```
{
    "strategy": "Simple Moving Average",
    "asset": "LTC/USD",
    "start_date": "2024-11-30",
    "end_date": "2025-01-23",
    "initial_capital": 10000,
    "interval": "15m",
    "strategy_params": {}
}
```
