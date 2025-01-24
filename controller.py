from flask import Blueprint, request, jsonify
from extensions import db
from models import BacktestStrategy
from strategies import TradingStrategies
from marshmallow import ValidationError
from datetime import datetime

backtest_bp = Blueprint('backtest', __name__)

# Strategy mapping
STRATEGIES = {
    'MACD Crossover': TradingStrategies.macd_crossover_strategy,
    'Simple Moving Average': TradingStrategies.moving_average_strategy
}


@backtest_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """
    Endpoint to run and save a trading strategy backtest
    """
    try:
        # Validate incoming data
        data = request.get_json()

        # Validate strategy exists
        strategy_name = data.get('strategy')
        if strategy_name not in STRATEGIES:
            return jsonify({'error': 'Invalid strategy'}), 400

        # Fetch price data
        try:
            price_data = TradingStrategies.fetch_price_data(
                data['asset'],
                data['start_date'],
                data['end_date']
            )
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        # Run backtest
        strategy_func = STRATEGIES[strategy_name]
        backtest_results = strategy_func(
            price_data,
            data.get('strategy_params', {}),
            data.get('initial_capital', 10000)
        )

        # Create and save backtest record
        backtest = BacktestStrategy(
            strategy=strategy_name,
            asset=data['asset'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            initial_capital=data.get('initial_capital', 10000),
            strategy_params=data.get('strategy_params', {}),
            backtest_results=backtest_results
        )

        db.session.add(backtest)
        db.session.commit()

        return jsonify({
            'backtest_id': backtest.id,
            'results': backtest_results
        }), 201

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/backtests', methods=['GET'])
def list_backtests():
    """
    Retrieve all saved backtest strategies
    """
    backtests = BacktestStrategy.query.all()
    return jsonify([{
        'id': bt.id,
        'strategy': bt.strategy,
        'asset': bt.asset,
        'start_date': bt.start_date.isoformat(),
        'end_date': bt.end_date.isoformat(),
        'final_portfolio_value': bt.backtest_results.get('final_portfolio_value') if bt.backtest_results else None
    } for bt in backtests]), 200
