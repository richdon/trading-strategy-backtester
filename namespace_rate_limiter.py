from flask_restx import Namespace, Resource, fields

# Create namespace
live_trading_ns = Namespace(
    'live',
    description='Live trading strategy operations',
    path='/live'
)

# Rate limit models
rate_limit_info = live_trading_ns.model('RateLimitInfo', {
    'remaining_api_calls': fields.Integer(
        description='Number of API calls remaining in current window',
        example=25
    ),
    'max_api_calls_per_minute': fields.Integer(
        description='Maximum allowed API calls per minute',
        example=30
    ),
    'active_strategies': fields.Integer(
        description='Current number of active strategies',
        example=2
    ),
    'max_strategies': fields.Integer(
        description='Maximum allowed active strategies',
        example=5
    ),
    'reset_window_seconds': fields.Integer(
        description='Seconds until rate limit window resets',
        example=60
    )
})

error_response = live_trading_ns.model('ErrorResponse', {
    'error': fields.String(
        description='Error message',
        example='Rate limit exceeded. Please try again later.'
    )
})
