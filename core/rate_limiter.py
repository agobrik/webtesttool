"""
Advanced rate limiting implementation with multiple strategies
"""

import time
from typing import Dict
from dataclasses import dataclass
from loguru import logger


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests: int
    window_seconds: int
    strategy: str = "token_bucket"  # token_bucket, fixed_window, sliding_window


class TokenBucketLimiter:
    """
    Token bucket rate limiting algorithm

    Example:
        limiter = TokenBucketLimiter(capacity=100, refill_rate=10)
        if limiter.allow_request():
            # Process request
            pass
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket limiter

        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, cost: int = 1) -> bool:
        """Check if request is allowed"""
        self._refill()

        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def get_tokens(self) -> float:
        """Get current token count"""
        self._refill()
        return self.tokens


class FixedWindowLimiter:
    """
    Fixed window rate limiting

    Example:
        limiter = FixedWindowLimiter(max_requests=100, window=60)
        if limiter.allow_request("user_123"):
            # Process request
            pass
    """

    def __init__(self, max_requests: int, window: int):
        self.max_requests = max_requests
        self.window = window
        self.windows: Dict[str, Dict[int, int]] = {}

    def allow_request(self, key: str) -> bool:
        """Check if request is allowed"""
        now = int(time.time())
        window_key = now // self.window

        if key not in self.windows:
            self.windows[key] = {}

        # Clean old windows
        self.windows[key] = {
            k: v for k, v in self.windows[key].items()
            if k >= window_key - 1
        }

        current_count = self.windows[key].get(window_key, 0)

        if current_count >= self.max_requests:
            return False

        self.windows[key][window_key] = current_count + 1
        return True


class SlidingWindowLimiter:
    """
    Sliding window rate limiting (more accurate)

    Example:
        limiter = SlidingWindowLimiter(max_requests=100, window=60)
        if limiter.allow_request("user_123"):
            # Process request
            pass
    """

    def __init__(self, max_requests: int, window: int):
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, list] = {}

    def allow_request(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()

        if key not in self.requests:
            self.requests[key] = []

        # Remove old requests outside window
        cutoff = now - self.window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]

        if len(self.requests[key]) >= self.max_requests:
            return False

        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests"""
        if key not in self.requests:
            return self.max_requests

        now = time.time()
        cutoff = now - self.window
        active = sum(1 for req in self.requests[key] if req > cutoff)
        return max(0, self.max_requests - active)


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on server load

    Example:
        limiter = AdaptiveRateLimiter(base_limit=100, window=60)
        limiter.set_load_factor(0.8)  # 80% load
        if limiter.allow_request("user_123"):
            # Process request
            pass
    """

    def __init__(self, base_limit: int, window: int):
        self.base_limit = base_limit
        self.window = window
        self.load_factor = 1.0  # 1.0 = normal, 0.5 = half capacity
        self.limiter = SlidingWindowLimiter(base_limit, window)

    def set_load_factor(self, factor: float):
        """Set load factor (0.0 to 1.0)"""
        self.load_factor = max(0.1, min(1.0, factor))
        adjusted_limit = int(self.base_limit * self.load_factor)
        self.limiter = SlidingWindowLimiter(adjusted_limit, self.window)

    def allow_request(self, key: str) -> bool:
        """Check if request is allowed"""
        return self.limiter.allow_request(key)


class RateLimitManager:
    """
    Manage multiple rate limiters

    Example:
        manager = RateLimitManager()
        manager.add_limiter("api", RateLimitConfig(max_requests=100, window_seconds=60))

        if manager.check_limit("api", "user_123"):
            # Process request
            pass
    """

    def __init__(self):
        self.limiters: Dict[str, tuple] = {}

    def add_limiter(self, name: str, config: RateLimitConfig):
        """Add a rate limiter"""
        if config.strategy == "token_bucket":
            limiter = TokenBucketLimiter(
                capacity=config.max_requests,
                refill_rate=config.max_requests / config.window_seconds
            )
        elif config.strategy == "fixed_window":
            limiter = FixedWindowLimiter(
                max_requests=config.max_requests,
                window=config.window_seconds
            )
        elif config.strategy == "sliding_window":
            limiter = SlidingWindowLimiter(
                max_requests=config.max_requests,
                window=config.window_seconds
            )
        else:
            raise ValueError(f"Unknown strategy: {config.strategy}")

        self.limiters[name] = (limiter, config)
        logger.info(f"Rate limiter '{name}' added: {config}")

    def check_limit(self, limiter_name: str, key: str) -> bool:
        """Check if request is allowed"""
        if limiter_name not in self.limiters:
            logger.warning(f"Rate limiter '{limiter_name}' not found")
            return True

        limiter, _ = self.limiters[limiter_name]

        if isinstance(limiter, TokenBucketLimiter):
            allowed = limiter.allow_request()
        else:
            allowed = limiter.allow_request(key)

        if not allowed:
            logger.warning(f"Rate limit exceeded: {limiter_name} for {key}")

        return allowed
