from .rate_limiter_service import RateLimiter
from .trading_service import TradingService
from .scheduler_service import TradingScheduler

# Create singleton instances
rate_limiter = RateLimiter()
trading_service = TradingService()
trading_scheduler = TradingScheduler()
