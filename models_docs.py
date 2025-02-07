from flask_restx import fields, Model


def create_api_models(api):
    """
    Create and register all Swagger API models
    """

    # Base Models
    user_model = api.model('User', {
        'id': fields.String(
            description='User unique identifier',
            example='123e4567-e89b-12d3-a456-426614174000'
        ),
        'username': fields.String(
            required=True,
            description='Username',
            example='trading_user',
            min_length=3,
            max_length=50
        ),
        'email': fields.String(
            required=True,
            description='Email address',
            example='user@example.com'
        )
    })

    # Authentication Models
    register_request = api.model('RegisterRequest', {
        'username': fields.String(
            required=True,
            description='Username for the new account',
            example='trading_user',
            min_length=3,
            max_length=50
        ),
        'email': fields.String(
            required=True,
            description='Email address',
            example='user@example.com'
        ),
        'password': fields.String(
            required=True,
            description='Account password',
            example='securepass123',
            min_length=8
        )
    })

    login_request = api.model('LoginRequest', {
        'username': fields.String(
            required=True,
            description='Username or email',
            example='trading_user'
        ),
        'password': fields.String(
            required=True,
            description='Account password',
            example='securepass123'
        )
    })

    auth_response = api.model('AuthResponse', {
        'access_token': fields.String(
            description='JWT access token',
            example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
        ),
        'user': fields.Nested(user_model)
    })

    # Trading Strategy Models
    strategy_params_macd = api.model('MACDParams', {
        'fast_period': fields.Integer(
            description='Fast period for MACD calculation',
            example=12,
            min=1
        ),
        'slow_period': fields.Integer(
            description='Slow period for MACD calculation',
            example=26,
            min=1
        ),
        'signal_period': fields.Integer(
            description='Signal period for MACD calculation',
            example=9,
            min=1
        )
    })

    strategy_params_ma = api.model('MovingAverageParams', {
        'short_period': fields.Integer(
            description='Short period for MA calculation',
            example=50,
            min=1
        ),
        'long_period': fields.Integer(
            description='Long period for MA calculation',
            example=200,
            min=1
        )
    })

    backtest_request = api.model('BacktestRequest', {
        'strategy': fields.String(
            required=True,
            description='Trading strategy name',
            enum=['MACD Crossover', 'Simple Moving Average'],
            example='MACD Crossover'
        ),
        'asset': fields.String(
            required=True,
            description='Trading asset symbol',
            example='BTC/USDT'
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

    trade_model = api.model('Trade', {
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

    backtest_response = api.model('BacktestResponse', {
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

    error_model = api.model('Error', {
        'error': fields.String(
            description='Error message',
            example='Invalid parameters provided'
        ),
        'details': fields.Raw(
            description='Detailed error information',
            example={
                'strategy_params': 'Invalid MACD parameters'
            }
        )
    })

    return {
        'user': user_model,
        'register_request': register_request,
        'login_request': login_request,
        'auth_response': auth_response,
        'strategy_params_macd': strategy_params_macd,
        'strategy_params_ma': strategy_params_ma,
        'backtest_request': backtest_request,
        'trade_model': trade_model,
        'backtest_response': backtest_response,
        'error': error_model
    }
