from flask_restx import Namespace, fields

# Create namespace for live trading endpoints
live_trading_ns = Namespace(
    'live',
    description='Live trading strategy operations',
    path='/live'
)

# Models for request/response
strategy_status = live_trading_ns.model('StrategyStatus', {
    'strategy_id': fields.String(
        description='Strategy identifier',
        example='123e4567-e89b-12d3-a456-426614174000'
    ),
    'asset': fields.String(
        description='Trading asset symbol',
        example='BTC/USD'
    ),
    'strategy_type': fields.String(
        description='Type of trading strategy',
        example='MACD Crossover'
    ),
    'last_check': fields.DateTime(
        description='Last time strategy was checked',
        example='2024-02-01T14:30:00Z'
    ),
    'last_signal': fields.DateTime(
        description='Last time a signal was generated',
        example='2024-02-01T12:15:00Z'
    ),
    'error_count': fields.Integer(
        description='Number of consecutive errors',
        example=0
    ),
    'is_active': fields.Boolean(
        description='Whether the strategy is currently active',
        example=True
    ),
    'interval': fields.String(
        description='Trading interval',
        example='1h'
    )
})

start_live_request = live_trading_ns.model('StartLiveRequest', {
    'backtest_id': fields.String(
        required=True,
        description='ID of the backtest to use as template',
        example='123e4567-e89b-12d3-a456-426614174000'
    )
})

live_strategy_response = live_trading_ns.model('LiveStrategyResponse', {
    'message': fields.String(
        description='Response message',
        example='Live trading started successfully'
    ),
    'strategy_id': fields.String(
        description='ID of the created live strategy',
        example='123e4567-e89b-12d3-a456-426614174000'
    )
})

error_response = live_trading_ns.model('ErrorResponse', {
    'error': fields.String(
        description='Error message',
        example='Strategy not found or rate limit exceeded'
    )
})
