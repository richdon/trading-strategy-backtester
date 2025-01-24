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

# Default params mapping
DEFAULT_PARAMS = {
    'MACD Crossover': TradingStrategies.mac_d_crossover_params_by_interval,
    'Simple Moving Average': TradingStrategies.moving_average_params_by_interval
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
        if not (strategy_name := data.get('strategy')):
            return jsonify({'error': 'Invalid strategy'}), 400

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
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

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
        'params': bt.strategy_params,
        'asset': bt.asset,
        'interval': bt.interval,
        'start_date': bt.start_date.isoformat(),
        'end_date': bt.end_date.isoformat(),
        'initial_capital': bt.initial_capital,
        'final_portfolio_value': bt.backtest_results.get('final_portfolio_value') if bt.backtest_results else None
    } for bt in backtests]), 200
