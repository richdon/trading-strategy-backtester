from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import LiveTradingStrategy, BacktestStrategy, User
from extensions import db
from namespace_live_trading import live_trading_ns, start_live_request, live_strategy_response, error_response, \
    strategy_status
from services import rate_limiter, trading_service, trading_scheduler


@live_trading_ns.route('')
class LiveTradingResource(Resource):
    @live_trading_ns.expect(start_live_request)
    @live_trading_ns.response(201, 'Live trading started successfully', live_strategy_response)
    @live_trading_ns.response(400, 'Invalid request', error_response)
    @live_trading_ns.response(401, 'Unauthorized')
    @live_trading_ns.response(429, 'Rate limit exceeded', error_response)
    @live_trading_ns.doc(
        security='jwt',
        description='Start live trading based on a saved backtest strategy'
    )
    @jwt_required()
    def post(self):
        """
        Start live trading based on a saved backtest strategy

        Creates a new live trading strategy using configuration from an existing backtest.
        The strategy will run at specified intervals and generate trading signals.
        Rate limits apply.
        """
        try:
            current_user_id = get_jwt_identity()

            # Check rate limits
            can_proceed, message = rate_limiter.check_rate_limit(current_user_id)
            if not can_proceed:
                return {'error': message}, 429

            # Check strategy limits
            can_add, message = rate_limiter.can_add_strategy(current_user_id)
            if not can_add:
                return {'error': message}, 400

            data = request.get_json()
            backtest_id = data.get('backtest_id')

            # Validate backtest exists and belongs to user
            backtest = BacktestStrategy.query.filter_by(
                id=backtest_id,
                user_id=current_user_id
            ).first()

            if not backtest:
                return {'error': 'Backtest not found'}, 404

            # Create live trading strategy
            live_strategy = LiveTradingStrategy(
                user_id=current_user_id,
                backtest_id=backtest_id,
                strategy=backtest.strategy,
                asset=backtest.asset,
                interval=backtest.interval,
                initial_capital=backtest.initial_capital,
                strategy_params=backtest.strategy_params,
                is_active=True
            )

            db.session.add(live_strategy)
            db.session.commit()

            # Start the strategy
            trading_scheduler.add_strategy(
                strategy_id=live_strategy.id,
                interval=live_strategy.interval
            )

            return {
                'message': 'Live trading started successfully',
                'strategy_id': live_strategy.id
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @live_trading_ns.response(200, 'Success', [strategy_status])
    @live_trading_ns.response(401, 'Unauthorized')
    @live_trading_ns.doc(
        security='jwt',
        description='Retrieve all active live trading strategies for the current user'
    )
    @jwt_required()
    def get(self):
        """
        List all active live trading strategies for the current user

        Returns details about all running strategies including their current status,
        last check time, and any error conditions.
        """
        try:
            current_user_id = get_jwt_identity()
            strategies = LiveTradingStrategy.query.filter_by(
                user_id=current_user_id,
                is_active=True
            ).all()

            status_list = []
            for strategy in strategies:
                status = trading_service.strategy_manager.strategy_statuses.get(strategy.id)
                if status:
                    status_list.append({
                        'strategy_id': strategy.id,
                        'asset': strategy.asset,
                        'strategy_type': strategy.strategy,
                        'last_check': status.last_check,
                        'last_signal': status.last_signal,
                        'error_count': status.error_count,
                        'is_active': status.is_active,
                        'interval': strategy.interval
                    })

            return status_list, 200

        except Exception as e:
            return {'error': str(e)}, 500


@live_trading_ns.route('/<strategy_id>')
@live_trading_ns.param('strategy_id', 'The strategy identifier')
class LiveTradingStrategyResource(Resource):
    @live_trading_ns.response(200, 'Strategy stopped successfully')
    @live_trading_ns.response(401, 'Unauthorized')
    @live_trading_ns.response(404, 'Strategy not found', error_response)
    @live_trading_ns.doc(security='jwt')
    @jwt_required()
    def delete(self, strategy_id):
        """
        Stop a running live trading strategy

        Deactivates the specified strategy and stops monitoring for trading signals.
        """
        try:
            current_user_id = get_jwt_identity()

            # Validate strategy exists and belongs to user
            strategy = LiveTradingStrategy.query.filter_by(
                id=strategy_id,
                user_id=current_user_id
            ).first()

            if not strategy:
                return {'error': 'Strategy not found'}, 404

            # Stop the strategy
            strategy.is_active = False
            db.session.commit()

            # Remove from scheduler
            trading_scheduler.remove_strategy(strategy_id)

            return {'message': 'Strategy stopped successfully'}, 200

        except Exception as e:
            return {'error': str(e)}, 500

    @live_trading_ns.route('/<strategy_id>')
    @live_trading_ns.param('strategy_id', 'The strategy identifier')
    class LiveTradingStrategyResource(Resource):
        @live_trading_ns.response(200, 'Success', strategy_status)
        @live_trading_ns.response(401, 'Unauthorized')
        @live_trading_ns.response(404, 'Strategy not found', error_response)
        @live_trading_ns.doc(security='jwt')
        @jwt_required()
        def get(self, strategy_id):
            try:
                current_user_id = get_jwt_identity()

                # Get strategy from database
                strategy = LiveTradingStrategy.query.filter_by(
                    id=strategy_id,
                    user_id=current_user_id
                ).first()

                if not strategy:
                    return {'error': 'Strategy not found'}, 404

                # Get status from strategy manager
                status = trading_service.strategy_manager.get_strategy_status(strategy_id)

                # If no status in manager, return database info
                if not status:
                    return {
                        'id': strategy.id,
                        'asset': strategy.asset,
                        'strategy': strategy.strategy,
                        'interval': strategy.interval,
                        'is_active': strategy.is_active,
                        'last_check_time': strategy.last_check_time,
                        'last_signal_time': strategy.last_signal_time,
                        'error_count': strategy.error_count,
                        'initial_capital': strategy.initial_capital,
                        'strategy_params': strategy.strategy_params
                    }, 200

                # Return status from manager
                return {
                    'id': strategy.id,
                    'asset': strategy.asset,
                    'strategy': strategy.strategy,
                    'interval': strategy.interval,
                    'is_active': status.is_active,
                    'last_check_time': status.last_check,
                    'last_signal_time': status.last_signal,
                    'error_count': status.error_count,
                    'initial_capital': strategy.initial_capital,
                    'strategy_params': strategy.strategy_params
                }, 200

            except Exception as e:
                return {'error': str(e)}, 500
