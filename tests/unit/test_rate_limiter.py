"""
Unit tests for rate limiting
"""

import pytest
import time
from core.rate_limiter import (
    TokenBucketLimiter,
    FixedWindowLimiter,
    SlidingWindowLimiter,
    RateLimitConfig,
    RateLimitManager
)


class TestTokenBucketLimiter:
    """Tests for token bucket rate limiter"""

    def test_initialization(self):
        """Test limiter initialization"""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)
        assert limiter.capacity == 10
        assert limiter.refill_rate == 1.0
        assert limiter.tokens == 10

    def test_allow_request(self):
        """Test basic request allowing"""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)

        # Should allow first 10 requests
        for _ in range(10):
            assert limiter.allow_request()

        # Should deny 11th request
        assert not limiter.allow_request()

    def test_token_refill(self):
        """Test token refill over time"""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=10.0)

        # Consume all tokens
        for _ in range(10):
            limiter.allow_request()

        # Wait for refill
        time.sleep(0.5)  # Should refill ~5 tokens

        # Should allow some requests again
        assert limiter.allow_request()

    def test_cost_based_limiting(self):
        """Test limiting with different costs"""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)

        # Request with cost of 5
        assert limiter.allow_request(cost=5)
        # Should have 5 tokens left
        assert limiter.allow_request(cost=5)
        # Should be empty now
        assert not limiter.allow_request()


class TestFixedWindowLimiter:
    """Tests for fixed window rate limiter"""

    def test_initialization(self):
        """Test limiter initialization"""
        limiter = FixedWindowLimiter(max_requests=10, window=60)
        assert limiter.max_requests == 10
        assert limiter.window == 60

    def test_allow_request(self):
        """Test basic request allowing"""
        limiter = FixedWindowLimiter(max_requests=5, window=60)

        # Should allow 5 requests
        for _ in range(5):
            assert limiter.allow_request("user_1")

        # Should deny 6th request
        assert not limiter.allow_request("user_1")

    def test_different_keys(self):
        """Test limiting per key"""
        limiter = FixedWindowLimiter(max_requests=3, window=60)

        # User 1
        for _ in range(3):
            assert limiter.allow_request("user_1")
        assert not limiter.allow_request("user_1")

        # User 2 should have separate limit
        for _ in range(3):
            assert limiter.allow_request("user_2")
        assert not limiter.allow_request("user_2")


class TestSlidingWindowLimiter:
    """Tests for sliding window rate limiter"""

    def test_initialization(self):
        """Test limiter initialization"""
        limiter = SlidingWindowLimiter(max_requests=10, window=60)
        assert limiter.max_requests == 10
        assert limiter.window == 60

    def test_allow_request(self):
        """Test basic request allowing"""
        limiter = SlidingWindowLimiter(max_requests=5, window=1)

        # Should allow 5 requests
        for _ in range(5):
            assert limiter.allow_request("user_1")

        # Should deny 6th request
        assert not limiter.allow_request("user_1")

    def test_window_sliding(self):
        """Test sliding window behavior"""
        limiter = SlidingWindowLimiter(max_requests=3, window=1)

        # Make 3 requests
        for _ in range(3):
            assert limiter.allow_request("user_1")

        # Should be limited
        assert not limiter.allow_request("user_1")

        # Wait for window to slide
        time.sleep(1.1)

        # Should allow new requests
        assert limiter.allow_request("user_1")

    def test_get_remaining(self):
        """Test getting remaining requests"""
        limiter = SlidingWindowLimiter(max_requests=5, window=60)

        assert limiter.get_remaining("user_1") == 5

        limiter.allow_request("user_1")
        assert limiter.get_remaining("user_1") == 4

        limiter.allow_request("user_1")
        limiter.allow_request("user_1")
        assert limiter.get_remaining("user_1") == 2


class TestRateLimitManager:
    """Tests for rate limit manager"""

    def test_add_limiter(self):
        """Test adding limiters"""
        manager = RateLimitManager()

        config = RateLimitConfig(
            max_requests=100,
            window_seconds=60,
            strategy="sliding_window"
        )

        manager.add_limiter("api", config)
        assert "api" in manager.limiters

    def test_check_limit(self):
        """Test checking limits"""
        manager = RateLimitManager()

        config = RateLimitConfig(
            max_requests=3,
            window_seconds=60,
            strategy="sliding_window"
        )

        manager.add_limiter("api", config)

        # Should allow 3 requests
        for _ in range(3):
            assert manager.check_limit("api", "user_1")

        # Should deny 4th request
        assert not manager.check_limit("api", "user_1")

    def test_unknown_limiter(self):
        """Test behavior with unknown limiter"""
        manager = RateLimitManager()

        # Should return True for unknown limiter (fail open)
        assert manager.check_limit("unknown", "user_1")
