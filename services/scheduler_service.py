from flask_apscheduler import APScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import threading
from typing import Dict, Optional


class TradingScheduler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TradingScheduler, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.scheduler = APScheduler()
        self.trading_service = None
        self.logger = logging.getLogger(__name__)

        # Interval mapping (trading interval -> seconds)
        self.INTERVALS = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }

        self._initialized = True

    def init_app(self, app, trading_service):
        """Initialize scheduler with Flask app and trading service"""
        self.trading_service = trading_service

        # Configure scheduler
        app.config['SCHEDULER_API_ENABLED'] = True
        app.config['SCHEDULER_TIMEZONE'] = "UTC"

        # Initialize and start scheduler
        self.scheduler.init_app(app)
        self.scheduler.start()

        self.logger.info("Trading scheduler initialized")

    def add_strategy(self, strategy_id: str, interval: str) -> bool:
        """
        Add a new strategy to the scheduler

        Args:
            strategy_id: The unique identifier of the strategy
            interval: Trading interval (e.g., '1m', '5m', '1h')

        Returns:
            bool: True if strategy was added successfully
        """
        try:
            # Get interval in seconds
            seconds = self.INTERVALS.get(interval)
            if not seconds:
                self.logger.error(f"Invalid interval: {interval}")
                return False

            # Create job ID
            job_id = f'strategy_{strategy_id}'

            # Add job with interval trigger
            self.scheduler.add_job(
                id=job_id,
                func=self.trading_service.check_signals,
                trigger=IntervalTrigger(seconds=seconds),
                args=[strategy_id],
                replace_existing=True,
                misfire_grace_time=seconds  # Allow misfires within one interval
            )

            self.logger.info(f"Added strategy {strategy_id} to scheduler with {interval} interval")
            return True

        except Exception as e:
            self.logger.error(f"Error adding strategy to scheduler: {str(e)}")
            return False

    def remove_strategy(self, strategy_id: str) -> bool:
        """
        Remove a strategy from the scheduler

        Args:
            strategy_id: The unique identifier of the strategy

        Returns:
            bool: True if strategy was removed successfully
        """
        try:
            job_id = f'strategy_{strategy_id}'
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                self.logger.info(f"Removed strategy {strategy_id} from scheduler")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error removing strategy from scheduler: {str(e)}")
            return False

    def get_strategy_status(self, strategy_id: str) -> Optional[Dict]:
        """
        Get the current status of a scheduled strategy

        Args:
            strategy_id: The unique identifier of the strategy

        Returns:
            Optional[Dict]: Strategy status information or None if not found
        """
        try:
            job_id = f'strategy_{strategy_id}'
            job = self.scheduler.get_job(job_id)

            if not job:
                return None

            return {
                'strategy_id': strategy_id,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'interval': str(job.trigger),
                'running': job.next_run_time is not None
            }

        except Exception as e:
            self.logger.error(f"Error getting strategy status: {str(e)}")
            return None

    def get_all_running_strategies(self) -> Dict[str, Dict]:
        """
        Get information about all running strategies

        Returns:
            Dict[str, Dict]: Dictionary of strategy_id -> status information
        """
        running_jobs = {}
        try:
            for job in self.scheduler.get_jobs():
                if job.id.startswith('strategy_'):
                    strategy_id = job.id.replace('strategy_', '')
                    running_jobs[strategy_id] = {
                        'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                        'interval': str(job.trigger),
                        'running': job.next_run_time is not None
                    }
            return running_jobs

        except Exception as e:
            self.logger.error(f"Error getting running strategies: {str(e)}")
            return {}

    def pause_strategy(self, strategy_id: str) -> bool:
        """
        Pause a running strategy

        Args:
            strategy_id: The unique identifier of the strategy

        Returns:
            bool: True if strategy was paused successfully
        """
        try:
            job_id = f'strategy_{strategy_id}'
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.pause_job(job_id)
                self.logger.info(f"Paused strategy {strategy_id}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error pausing strategy: {str(e)}")
            return False

    def resume_strategy(self, strategy_id: str) -> bool:
        """
        Resume a paused strategy

        Args:
            strategy_id: The unique identifier of the strategy

        Returns:
            bool: True if strategy was resumed successfully
        """
        try:
            job_id = f'strategy_{strategy_id}'
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.resume_job(job_id)
                self.logger.info(f"Resumed strategy {strategy_id}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error resuming strategy: {str(e)}")
            return False
