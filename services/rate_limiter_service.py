from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import threading
import logging
from models import LiveTradingStrategy


class RateLimiter:
    """
    Rate limiter to control API usage and number of active strategies per user.
    Thread-safe implementation using in-memory storage.
    """

    def __init__(self):
        # Track API calls per user: user_id -> list of timestamps
        self._user_calls: Dict[str, List[datetime]] = defaultdict(list)

        # Thread safety lock
        self._lock = threading.Lock()

        # Configure logger
        self.logger = logging.getLogger(__name__)

        # Rate limiting configuration
        self.MAX_STRATEGIES_PER_USER = 5
        self.MAX_CALLS_PER_MINUTE = 30
        self.CALL_WINDOW = timedelta(minutes=1)

        # Auto cleanup old data periodically
        self._cleanup_old_data()

    def can_add_strategy(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if user can add another strategy

        Args:
            user_id (str): The user's unique identifier

        Returns:
            Tuple[bool, str]: (can_add, message)
            - can_add: True if user can add another strategy, False otherwise
            - message: Explanation message if can_add is False, empty string otherwise
        """
        try:
            # Query active strategies for the user
            active_strategies = LiveTradingStrategy.query.filter_by(
                user_id=user_id,
                is_active=True
            ).count()

            if active_strategies >= self.MAX_STRATEGIES_PER_USER:
                return False, (
                    f"Maximum of {self.MAX_STRATEGIES_PER_USER} active "
                    f"strategies allowed. Currently running: {active_strategies}"
                )
            return True, ""

        except Exception as e:
            self.logger.error(f"Error checking strategy limit for user {user_id}: {str(e)}")
            # If there's a database error, err on the side of caution
            return False, "Error checking strategy limit. Please try again later."

    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if user has exceeded API rate limits

        Args:
            user_id (str): The user's unique identifier

        Returns:
            Tuple[bool, str]: (allowed, message)
            - allowed: True if request is allowed, False if rate limit exceeded
            - message: Error message if rate limit exceeded, empty string otherwise
        """
        with self._lock:
            try:
                now = datetime.utcnow()

                # Remove old calls outside the window
                self._user_calls[user_id] = [
                    call_time for call_time in self._user_calls[user_id]
                    if now - call_time <= self.CALL_WINDOW
                ]

                # Check if user has exceeded rate limit
                if len(self._user_calls[user_id]) >= self.MAX_CALLS_PER_MINUTE:
                    window_end = min(self._user_calls[user_id]) + self.CALL_WINDOW
                    seconds_remaining = int((window_end - now).total_seconds())

                    return False, (
                        f"Rate limit exceeded. Maximum {self.MAX_CALLS_PER_MINUTE} "
                        f"calls per {self.CALL_WINDOW.seconds // 60} minute(s). "
                        f"Please try again in {seconds_remaining} seconds."
                    )

                # Record this call
                self._user_calls[user_id].append(now)
                return True, ""

            except Exception as e:
                self.logger.error(f"Error checking rate limit for user {user_id}: {str(e)}")
                # If there's an error, allow the request but log it
                return True, ""

    def get_remaining_calls(self, user_id: str) -> int:
        """
        Get number of remaining API calls for user

        Args:
            user_id (str): The user's unique identifier

        Returns:
            int: Number of remaining API calls in current window
        """
        with self._lock:
            try:
                now = datetime.utcnow()
                # Count recent calls within window
                recent_calls = len([
                    call_time for call_time in self._user_calls[user_id]
                    if now - call_time <= self.CALL_WINDOW
                ])
                return max(0, self.MAX_CALLS_PER_MINUTE - recent_calls)
            except Exception as e:
                self.logger.error(f"Error getting remaining calls for user {user_id}: {str(e)}")
                return 0

    def get_strategy_count(self, user_id: str) -> Tuple[int, int]:
        """
        Get current active strategy count and maximum allowed

        Args:
            user_id (str): The user's unique identifier

        Returns:
            Tuple[int, int]: (current_count, max_allowed)
            - current_count: Number of currently active strategies
            - max_allowed: Maximum number of strategies allowed
        """
        try:
            active_count = LiveTradingStrategy.query.filter_by(
                user_id=user_id,
                is_active=True
            ).count()
            return active_count, self.MAX_STRATEGIES_PER_USER

        except Exception as e:
            self.logger.error(f"Error getting strategy count for user {user_id}: {str(e)}")
            return 0, self.MAX_STRATEGIES_PER_USER

    def _cleanup_old_data(self) -> None:
        """
        Remove old API call data to prevent memory growth
        This is called automatically during initialization
        """
        with self._lock:
            try:
                now = datetime.utcnow()
                for user_id in list(self._user_calls.keys()):
                    # Remove calls outside the window
                    self._user_calls[user_id] = [
                        call_time for call_time in self._user_calls[user_id]
                        if now - call_time <= self.CALL_WINDOW
                    ]
                    # Remove empty user entries
                    if not self._user_calls[user_id]:
                        del self._user_calls[user_id]

            except Exception as e:
                self.logger.error(f"Error during data cleanup: {str(e)}")

    def reset_user_limits(self, user_id: str) -> None:
        """
        Reset rate limits for a specific user
        Useful for testing or administrative purposes

        Args:
            user_id (str): The user's unique identifier
        """
        with self._lock:
            if user_id in self._user_calls:
                del self._user_calls[user_id]

    def get_usage_metrics(self, user_id: str) -> Dict[str, any]:
        """
        Get detailed usage metrics for a user

        Args:
            user_id (str): The user's unique identifier

        Returns:
            Dict containing:
            - remaining_calls: Number of remaining API calls
            - total_calls: Total calls made in current window
            - active_strategies: Number of active strategies
            - window_reset: Datetime when current window resets
        """
        with self._lock:
            try:
                now = datetime.utcnow()
                recent_calls = [
                    call_time for call_time in self._user_calls[user_id]
                    if now - call_time <= self.CALL_WINDOW
                ]

                # Calculate window reset time
                window_reset = (
                    min(recent_calls) + self.CALL_WINDOW if recent_calls
                    else now + self.CALL_WINDOW
                )

                active_strategies, _ = self.get_strategy_count(user_id)

                return {
                    'remaining_calls': max(0, self.MAX_CALLS_PER_MINUTE - len(recent_calls)),
                    'total_calls': len(recent_calls),
                    'active_strategies': active_strategies,
                    'window_reset': window_reset.isoformat(),
                    'max_calls_per_minute': self.MAX_CALLS_PER_MINUTE,
                    'max_strategies': self.MAX_STRATEGIES_PER_USER
                }

            except Exception as e:
                self.logger.error(f"Error getting usage metrics for user {user_id}: {str(e)}")
                return {
                    'error': 'Error retrieving usage metrics',
                    'max_calls_per_minute': self.MAX_CALLS_PER_MINUTE,
                    'max_strategies': self.MAX_STRATEGIES_PER_USER
                }