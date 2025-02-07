from flask_restx import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from marshmallow import ValidationError
from extensions import db
from models import User, BacktestStrategy
from namespace_backtest import backtest_ns, backtest_request, backtest_response, backtest_summary
from strategies import TradingStrategies

# Strategy mapping
STRATEGIES = {
    'MACD Crossover': TradingStrategies.macd_crossover_strategy,
    'Simple Moving Average': TradingStrategies.moving_average_strategy
}

# Default params mapping
DEFAULT_PARAMS = {
    'MACD Crossover': TradingStrategies.mac_d_crossover_params_by_interval,
    'Simple Moving Average': TradingStrategies.moving_average_params_by_interval
}


@backtest_ns.route('')
class Backtest(Resource):
    @backtest_ns.expect(backtest_request)
    @backtest_ns.response(201, 'Backtest executed successfully', backtest_response)
    @backtest_ns.response(400, 'Invalid parameters')
    @backtest_ns.response(401, 'Unauthorized')
    @backtest_ns.doc(security='jwt')
    @jwt_required()
    def post(self):
        """
        Execute a new trading strategy backtest

        Run a backtest simulation using the specified trading strategy and parameters.
        Returns detailed results including all trades and performance metrics.
        """
        try:
            # Get current user
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return {'error': 'User not found'}, 404

            # Validate incoming data
            data = request.get_json()

            # Validate strategy exists
            if not (strategy_name := data.get('strategy')):
                return {'error': 'Invalid strategy'}, 400

            asset = data['asset']
            start_date = data['start_date']
            end_date = data['end_date']
            interval = data.get('interval', '1d')
            initial_capital = data.get('initial_capital', 10000)
            params = data.get('strategy_params') or DEFAULT_PARAMS[strategy_name](interval)

            # Fetch price data
            try:
                price_data = TradingStrategies.fetch_price_data(
                    asset,
                    start_date,
                    end_date,
                    interval
                )
                if isinstance(price_data, list):
                    return {'error': 'No data for selected ticker or timeframe'}, 400
            except ValidationError as e:
                return {'error': str(e)}, 400

            # Run backtest
            strategy_func = STRATEGIES[strategy_name]
            backtest_results = strategy_func(
                price_data,
                initial_capital,
                interval,
                params
            )
            # Create and save backtest record
            backtest = BacktestStrategy(
                user_id=current_user_id,
                strategy=strategy_name,
                asset=asset,
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                initial_capital=initial_capital,
                strategy_params=params,
                interval=interval,
                backtest_results=backtest_results
            )

            db.session.add(backtest)
            db.session.commit()
            backtest_results['asset'] = asset
            return {
                'backtest_id': backtest.id,
                'results': backtest_results,
            }, 201

        except ValidationError as err:
            return err.messages, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


@backtest_ns.route('/list')
class Backtest(Resource):
    @backtest_ns.response(200, 'Success', [backtest_summary])
    @backtest_ns.response(401, 'Unauthorized')
    @backtest_ns.doc(
        security='jwt',
        description='Retrieve all backtests for the current user'
    )
    @jwt_required()
    def get(self):
        """
        Retrieve saved backtest strategies for current user
        """
        current_user_id = get_jwt_identity()

        # Fetch only the current user's backtests
        backtests = BacktestStrategy.query.filter_by(user_id=current_user_id).all()

        return [{
            'id': bt.id,
            'strategy': bt.strategy,
            'params': bt.strategy_params,
            'asset': bt.asset,
            'interval': bt.interval,
            'start_date': bt.start_date.isoformat(),
            'end_date': bt.end_date.isoformat(),
            'initial_capital': bt.initial_capital,
            'final_portfolio_value': bt.backtest_results.get('final_portfolio_value') if bt.backtest_results else None
        } for bt in backtests], 200


@backtest_ns.route('/greatest-return')
class BacktestGreatestReturn(Resource):
    @backtest_ns.response(200, 'Success', backtest_summary)
    @backtest_ns.response(401, 'Unauthorized')
    @backtest_ns.doc(
        security='jwt',
        description='Retrieve backtest for the current user with greatest return'
    )
    @jwt_required()
    def get(self):
        """
        Retrieve saved backtest strategies for current user that has the greatest return
        """
        current_user_id = get_jwt_identity()

        # Fetch only the current user's backtests
        bt = BacktestStrategy.query.filter_by(user_id=current_user_id).order_by(
            (BacktestStrategy.backtest_results['final_portfolio_value'] -
             BacktestStrategy.initial_capital).desc()).first()
        return {
            'id': bt.id,
            'strategy': bt.strategy,
            'params': bt.strategy_params,
            'asset': bt.asset,
            'interval': bt.interval,
            'start_date': bt.start_date.isoformat(),
            'end_date': bt.end_date.isoformat(),
            'initial_capital': bt.initial_capital,
            'final_portfolio_value': bt.backtest_results.get('final_portfolio_value') if bt.backtest_results else None
        }, 200


# Error handlers
@backtest_ns.errorhandler(ValueError)
def handle_validation_error(error):
    """Handle validation errors"""
    return {'error': str(error)}, 400


@backtest_ns.errorhandler(Exception)
def handle_generic_error(error):
    """Handle generic errors"""
    return {'error': f'Internal server error {str(error)}'}, 500
