from flask_restx import Api
from flask import Blueprint, request
from auth import auth_ns
from backtest import backtest_ns
from models_docs import create_api_models


def initialize_routes():
    """
    Initialize and configure all API routes with Swagger documentation
    """
    # Create Blueprint for Swagger UI
    blueprint = Blueprint('api', __name__)

    # Initialize API with blueprint
    api = Api(
        blueprint,
        version='1.0',
        title='Trading Bot API',
        description="""
        Trading bot API with authentication and backtesting capabilities.

        Features:
        * User registration and authentication
        * Multiple trading strategies
        * Customizable backtest parameters
        * Historical data analysis
        * Performance metrics
        """,
        doc='/docs',  # Swagger UI will be available at /api/docs
        authorizations={
            'jwt': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
            }
        },
        security='jwt'
    )

    # Add namespaces
    api.add_namespace(auth_ns)
    api.add_namespace(backtest_ns)

    # Global error handlers
    @api.errorhandler(Exception)
    def handle_global_error(error):
        """Global error handler for unhandled exceptions"""
        return {
            'message': 'Internal server error',
            'error': str(error)
        }, 500

    @api.errorhandler(ValueError)
    def handle_validation_error(error):
        """Handler for validation errors"""
        return {
            'message': 'Validation error',
            'error': str(error)
        }, 400

    # API documentation descriptions
    strategy_descriptions = {
        'MACD Crossover': {
            'description': 'Moving Average Convergence Divergence (MACD) strategy',
            'parameters': [
                'fast_period: Period for fast EMA calculation',
                'slow_period: Period for slow EMA calculation',
                'signal_period: Period for signal line calculation'
            ],
            'typical_values': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            }
        },
        'Simple Moving Average': {
            'description': 'Simple Moving Average (SMA) Crossover strategy',
            'parameters': [
                'short_period: Period for short-term moving average',
                'long_period: Period for long-term moving average'
            ],
            'typical_values': {
                'short_period': 50,
                'long_period': 200
            }
        }
    }

    # API metadata
    api.description += "\n\nAvailable Trading Strategies:\n"
    for strategy, details in strategy_descriptions.items():
        api.description += f"\n### {strategy}\n"
        api.description += f"{details['description']}\n"
        api.description += "\nParameters:\n"
        for param in details['parameters']:
            api.description += f"* {param}\n"
        api.description += "\nTypical Values:\n"
        for param, value in details['typical_values'].items():
            api.description += f"* {param}: {value}\n"

    # Custom response definitions
    api.response(401, 'Unauthorized - Invalid or missing authentication token')
    api.response(403, 'Forbidden - Insufficient permissions')
    api.response(404, 'Not Found - Requested resource does not exist')
    api.response(500, 'Internal Server Error - Something went wrong on the server')

    # Custom request parsers
    pagination_parser = api.parser()
    pagination_parser.add_argument('page', type=int, location='args', default=1, help='Page number')
    pagination_parser.add_argument('per_page', type=int, location='args', default=10, help='Items per page')

    date_range_parser = api.parser()
    date_range_parser.add_argument('start_date', type=str, location='args', help='Start date (YYYY-MM-DD)')
    date_range_parser.add_argument('end_date', type=str, location='args', help='End date (YYYY-MM-DD)')

    # Add parsers to api object for reuse in endpoints
    api.pagination_parser = pagination_parser
    api.date_range_parser = date_range_parser

    return blueprint, api


def register_routes(app, blueprint):
    """
    Register routes with the Flask application
    """
    # Register blueprint with URL prefix
    app.register_blueprint(blueprint, url_prefix='/api')

    # Optional: Add CORS support
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    # Optional: Add request logging
    @app.before_request
    def log_request_info():
        app.logger.debug('Headers: %s', request.headers)
        app.logger.debug('Body: %s', request.get_data())


def configure_swagger_ui(app):
    """
    Configure Swagger UI settings
    """
    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'  # Expand/collapse API documentation
    app.config.SWAGGER_UI_OPERATION_ID = True  # Show operation IDs
    app.config.SWAGGER_UI_REQUEST_DURATION = True  # Show request duration
    app.config.RESTX_MASK_SWAGGER = False  # Don't mask sensitive data in examples