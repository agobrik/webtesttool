"""
Unit tests for Progress Tracker
"""

import pytest
from io import StringIO
from core.progress import ProgressTracker, SimpleProgressTracker, create_progress_tracker


class TestProgressTracker:
    """Test ProgressTracker functionality"""

    @pytest.fixture
    def tracker(self):
        """Create ProgressTracker instance"""
        return ProgressTracker()

    def test_tracker_initialization(self, tracker):
        """Test tracker initialization"""
        assert tracker.is_running is False
        assert len(tracker.tasks) == 0
        assert tracker.stats['pages_crawled'] == 0
        assert tracker.stats['tests_completed'] == 0

    def test_start_stop(self, tracker):
        """Test starting and stopping tracker"""
        tracker.start()
        assert tracker.is_running is True
        assert tracker.start_time is not None

        tracker.stop()
        assert tracker.is_running is False

    def test_add_task(self, tracker):
        """Test adding tasks"""
        tracker.start()

        task_id = tracker.add_task("test_task", total=100)

        assert "test_task" in tracker.tasks
        assert task_id is not None

        tracker.stop()

    def test_update_task(self, tracker):
        """Test updating task progress"""
        tracker.start()

        tracker.add_task("test_task", total=100)
        tracker.update_task("test_task", advance=10)
        tracker.update_task("test_task", advance=20)

        # Task should have progressed
        # (Cannot check exact progress without accessing internal state)

        tracker.stop()

    def test_complete_task(self, tracker):
        """Test completing task"""
        tracker.start()

        tracker.add_task("test_task", total=100)
        tracker.update_task("test_task", advance=50)
        tracker.complete_task("test_task")

        # Task should be completed
        tracker.stop()

    def test_update_stats(self, tracker):
        """Test updating statistics"""
        tracker.update_stat('pages_crawled', 10)
        tracker.update_stat('tests_completed', 5)

        assert tracker.stats['pages_crawled'] == 10
        assert tracker.stats['tests_completed'] == 5

    def test_increment_stats(self, tracker):
        """Test incrementing statistics"""
        tracker.increment_stat('pages_crawled', 1)
        tracker.increment_stat('pages_crawled', 2)
        tracker.increment_stat('findings_critical', 1)

        assert tracker.stats['pages_crawled'] == 3
        assert tracker.stats['findings_critical'] == 1

    def test_get_stats(self, tracker):
        """Test getting statistics"""
        tracker.update_stat('pages_crawled', 100)
        tracker.update_stat('findings_total', 15)

        stats = tracker.get_stats()

        assert stats['pages_crawled'] == 100
        assert stats['findings_total'] == 15
        assert isinstance(stats, dict)


class TestSimpleProgressTracker:
    """Test SimpleProgressTracker functionality"""

    @pytest.fixture
    def tracker(self):
        """Create SimpleProgressTracker instance"""
        return SimpleProgressTracker()

    def test_tracker_initialization(self, tracker):
        """Test tracker initialization"""
        assert len(tracker.tasks) == 0
        assert tracker.stats['pages_crawled'] == 0

    def test_add_task(self, tracker):
        """Test adding tasks"""
        tracker.add_task("test_task", total=100)

        assert "test_task" in tracker.tasks
        assert tracker.tasks["test_task"]['total'] == 100
        assert tracker.tasks["test_task"]['completed'] == 0

    def test_update_task(self, tracker):
        """Test updating task"""
        tracker.add_task("test_task", total=100)
        tracker.update_task("test_task", advance=10)

        assert tracker.tasks["test_task"]['completed'] == 10

        tracker.update_task("test_task", advance=20)
        assert tracker.tasks["test_task"]['completed'] == 30

    def test_update_stats(self, tracker):
        """Test updating statistics"""
        tracker.update_stat('pages_crawled', 50)
        tracker.update_stat('tests_completed', 10)

        assert tracker.stats['pages_crawled'] == 50
        assert tracker.stats['tests_completed'] == 10

    def test_increment_stats(self, tracker):
        """Test incrementing statistics"""
        tracker.increment_stat('pages_crawled', 5)
        tracker.increment_stat('pages_crawled', 3)

        assert tracker.stats['pages_crawled'] == 8


class TestProgressTrackerFactory:
    """Test progress tracker factory"""

    def test_create_rich_tracker(self):
        """Test creating Rich tracker"""
        try:
            tracker = create_progress_tracker(use_rich=True)
            assert isinstance(tracker, (ProgressTracker, SimpleProgressTracker))
        except ImportError:
            # Rich not available, should fall back
            tracker = create_progress_tracker(use_rich=True)
            assert isinstance(tracker, SimpleProgressTracker)

    def test_create_simple_tracker(self):
        """Test creating simple tracker"""
        tracker = create_progress_tracker(use_rich=False)
        assert isinstance(tracker, SimpleProgressTracker)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
