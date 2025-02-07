from flask_restx import Namespace, fields

backtest_ns = Namespace(
    'backtest',
    description='Trading strategy backtesting operations',
    path='/backtest'
)

# Import the strategy mappings
STRATEGIES = {
    'MACD Crossover': 'MACD-based trading strategy with customizable parameters',
    'Simple Moving Average': 'Moving average crossover strategy with customizable periods'
}

# Models for strategy parameters
macd_params = backtest_ns.model('MACDParameters', {
    'fast_period': fields.Integer(
        required=True,
        description='Fast period for MACD calculation',
        example=12,
        min=1
    ),
    'slow_period': fields.Integer(
        required=True,
        description='Slow period for MACD calculation',
        example=26,
        min=1
    ),
    'signal_period': fields.Integer(
        required=True,
        description='Signal period for MACD calculation',
        example=9,
        min=1
    )
})

ma_params = backtest_ns.model('MovingAverageParameters', {
    'short_period': fields.Integer(
        required=True,
        description='Short period for MA calculation',
        example=50,
        min=1
    ),
    'long_period': fields.Integer(
        required=True,
        description='Long period for MA calculation',
        example=200,
        min=1
    )
})

# Main backtest request model
backtest_request = backtest_ns.model('BacktestRequest', {
    'strategy': fields.String(
        required=True,
        description='Trading strategy to backtest',
        enum=list(STRATEGIES.keys()),
        example='MACD Crossover'
    ),
    'asset': fields.String(
        required=True,
        description='Trading asset symbol (e.g., BTC/USDT)',
        example='BTC/USD'
    ),
    'start_date': fields.String(
        required=True,
        description='Start date for backtest (YYYY-MM-DD)',
        example='2023-01-01'
    ),
    'end_date': fields.String(
        required=True,
        description='End date for backtest (YYYY-MM-DD)',
        example='2023-12-31'
    ),
    'interval': fields.String(
        required=True,
        description='Trading interval',
        enum=['1m', '5m', '15m', '1h', '4h', '1d', '1w'],
        example='1h'
    ),
    'initial_capital': fields.Float(
        required=True,
        description='Initial capital for backtesting',
        example=10000.0,
        min=0
    ),
    'strategy_params': fields.Raw(
        description='Strategy-specific parameters (MACD or MA)',
        example={
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
    )
})

# Trade model for individual trades in the backtest
trade_model = backtest_ns.model('Trade', {
    'date': fields.String(
        description='Trade timestamp',
        example='2023-01-01 14:30:00'
    ),
    'portfolio_value': fields.Float(
        description='Portfolio value after trade',
        example=10500.75
    ),
    'position': fields.Float(
        description='Position size',
        example=0.5
    ),
    'price': fields.Float(
        description='Asset price at trade',
        example=45000.00
    ),
    'capital': fields.Float(
        description='Available capital',
        example=5000.00
    ),
    'asset': fields.Float(
        description='Asset value',
        example=5500.75
    ),
    'trade': fields.String(
        description='Trade type',
        enum=['BUY', 'SELL', 'HOLD'],
        example='BUY'
    )
})

# Backtest response model
backtest_response = backtest_ns.model('BacktestResponse', {
    'backtest_id': fields.String(
        description='Unique identifier for the backtest',
        example='456e4567-e89b-12d3-a456-426614174000'
    ),
    'trades': fields.List(
        fields.Nested(trade_model),
        description='List of trades executed'
    ),
    'final_portfolio_value': fields.Float(
        description='Final portfolio value',
        example=12500.50
    ),
    'total_return_percentage': fields.Float(
        description='Total return percentage',
        example=25.0
    ),
    'sharpe_ratio': fields.Float(
        description='Sharpe ratio',
        example=1.5
    ),
    'interval': fields.String(
        description='Trading interval used',
        example='1h'
    ),
    'initial_capital': fields.Float(
        description='Initial capital used',
        example=10000.0
    )
})

# Backtest summary for list endpoint
backtest_summary = backtest_ns.model('BacktestSummary', {
    'id': fields.String(
        description='Backtest identifier',
        example='456e4567-e89b-12d3-a456-426614174000'
    ),
    'strategy': fields.String(
        description='Strategy name',
        example='MACD Crossover'
    ),
    'asset': fields.String(
        description='Trading asset',
        example='BTC/USD'
    ),
    'interval': fields.String(
        description='Trading interval',
        example='1h'
    ),
    'start_date': fields.String(
        description='Start date',
        example='2023-01-01'
    ),
    'end_date': fields.String(
        description='End date',
        example='2023-12-31'
    ),
    'initial_capital': fields.Float(
        description='Initial capital',
        example=10000.0
    ),
    'final_portfolio_value': fields.Float(
        description='Final portfolio value',
        example=12500.50
    )
})