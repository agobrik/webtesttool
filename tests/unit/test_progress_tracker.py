"""
Unit tests for Progress Tracker
"""

import pytest
import time
from utils.progress_tracker import ProgressTracker


@pytest.fixture
def progress():
    """Create progress tracker without live display for testing"""
    return ProgressTracker(enable_live_display=False)


@pytest.mark.unit
def test_progress_initialization(progress):
    """Test progress tracker initialization"""
    assert progress is not None
    assert progress.tasks == {}
    assert progress.stats['pages_crawled'] == 0
    assert progress.stats['tests_completed'] == 0
    assert progress.start_time is None


@pytest.mark.unit
def test_progress_start_stop(progress):
    """Test starting and stopping progress tracker"""
    progress.start()
    assert progress.start_time is not None

    progress.stop()
    # Should not raise an error


@pytest.mark.unit
def test_add_task(progress):
    """Test adding tasks"""
    progress.start()

    task_id = progress.add_task("test_task", total=100, description="Test Task")

    assert isinstance(task_id, int)
    assert "test_task" in progress.tasks
    assert progress.tasks["test_task"] == task_id


@pytest.mark.unit
def test_update_task(progress):
    """Test updating task progress"""
    progress.start()
    progress.add_task("test_task", total=100)

    # Update task
    progress.update_task("test_task", advance=10)

    # Verify task was updated (we can't directly check without accessing internals)
    # But we can verify it doesn't raise an error
    progress.update_task("test_task", advance=5)


@pytest.mark.unit
def test_complete_task(progress):
    """Test completing a task"""
    progress.start()
    progress.add_task("test_task", total=100)

    # Complete task
    progress.complete_task("test_task")

    # Verify completion (should not raise error)
    # The task should be marked as completed internally


@pytest.mark.unit
def test_update_stat(progress):
    """Test updating statistics"""
    # Update stat
    progress.update_stat('pages_crawled', 50)

    assert progress.stats['pages_crawled'] == 50

    # Update another stat
    progress.update_stat('tests_completed', 10)

    assert progress.stats['tests_completed'] == 10


@pytest.mark.unit
def test_increment_stat(progress):
    """Test incrementing statistics"""
    # Initial value
    assert progress.stats['pages_crawled'] == 0

    # Increment
    progress.increment_stat('pages_crawled', 1)
    assert progress.stats['pages_crawled'] == 1

    # Increment by 5
    progress.increment_stat('pages_crawled', 5)
    assert progress.stats['pages_crawled'] == 6


@pytest.mark.unit
def test_multiple_stats(progress):
    """Test updating multiple statistics"""
    progress.update_stat('pages_crawled', 100)
    progress.update_stat('forms_found', 20)
    progress.update_stat('api_endpoints', 15)
    progress.update_stat('findings_critical', 3)
    progress.update_stat('findings_high', 8)

    assert progress.stats['pages_crawled'] == 100
    assert progress.stats['forms_found'] == 20
    assert progress.stats['api_endpoints'] == 15
    assert progress.stats['findings_critical'] == 3
    assert progress.stats['findings_high'] == 8


@pytest.mark.unit
def test_get_stats_table(progress):
    """Test generating statistics table"""
    progress.start()
    progress.update_stat('pages_crawled', 50)
    progress.update_stat('tests_completed', 10)
    progress.update_stat('findings_high', 3)

    # Get stats table
    table = progress.get_stats_table()

    # Verify table is created
    assert table is not None
    assert table.title == "📊 Live Statistics"


@pytest.mark.unit
def test_get_current_status(progress):
    """Test getting current status panel"""
    progress.update_stat('status', 'Running tests')
    progress.update_stat('current_url', 'https://example.com')
    progress.update_stat('current_module', 'Security')

    # Get status panel
    panel = progress.get_current_status()

    assert panel is not None
    assert panel.title == "🎯 Current Status"


@pytest.mark.unit
def test_context_manager(progress):
    """Test using progress tracker as context manager"""
    with progress as p:
        assert p.start_time is not None
        assert p == progress

    # After exiting context, progress should be stopped
    # (we can't directly verify but it shouldn't raise error)


@pytest.mark.unit
def test_display_simple_progress(progress):
    """Test simple progress display"""
    # This should not raise an error in non-live mode
    progress.display_simple_progress("Testing", 50, 100)


@pytest.mark.unit
def test_log_message(progress):
    """Test logging messages"""
    # Should not raise error
    progress.log("Test message")
    progress.log("Warning message", style="yellow")
    progress.log("Error message", style="red")


@pytest.mark.unit
def test_display_final_summary(progress):
    """Test displaying final summary"""
    progress.start()
    progress.update_stat('pages_crawled', 100)
    progress.update_stat('tests_completed', 50)
    progress.update_stat('findings_critical', 2)
    progress.update_stat('findings_high', 5)

    # Should not raise error
    progress.display_final_summary()


@pytest.mark.unit
def test_multiple_tasks(progress):
    """Test managing multiple tasks"""
    progress.start()

    # Add multiple tasks
    progress.add_task("crawler", total=100, description="Crawling")
    progress.add_task("security", total=50, description="Security Tests")
    progress.add_task("performance", total=30, description="Performance Tests")

    # Update tasks
    progress.update_task("crawler", advance=10)
    progress.update_task("security", advance=5)
    progress.update_task("performance", advance=3)

    # Complete tasks
    progress.complete_task("crawler")
    progress.complete_task("security")
    progress.complete_task("performance")


@pytest.mark.unit
def test_update_nonexistent_stat(progress):
    """Test updating non-existent stat does nothing"""
    # This should not raise an error
    progress.update_stat('nonexistent_stat', 100)

    # Verify it's not in stats
    assert 'nonexistent_stat' not in progress.stats


@pytest.mark.unit
def test_increment_nonexistent_stat(progress):
    """Test incrementing non-existent stat does nothing"""
    # This should not raise an error
    progress.increment_stat('nonexistent_stat', 1)

    # Verify it's not in stats
    assert 'nonexistent_stat' not in progress.stats


@pytest.mark.unit
def test_stat_persistence(progress):
    """Test that stats persist through operations"""
    progress.update_stat('pages_crawled', 10)
    progress.update_stat('tests_completed', 5)

    # Add tasks
    progress.start()
    progress.add_task("test", total=100)

    # Stats should still be there
    assert progress.stats['pages_crawled'] == 10
    assert progress.stats['tests_completed'] == 5

    # Update more stats
    progress.increment_stat('pages_crawled', 5)
    assert progress.stats['pages_crawled'] == 15


@pytest.mark.unit
def test_create_live_display(progress):
    """Test creating live display layout"""
    # Even without live display enabled, should be able to create layout
    layout = progress.create_live_display()

    assert layout is not None
    # Check that named layouts can be accessed without errors
    assert layout["header"] is not None
    assert layout["body"] is not None
    assert layout["footer"] is not None


@pytest.mark.unit
def test_findings_tracking(progress):
    """Test tracking findings by severity"""
    progress.increment_stat('findings_critical', 2)
    progress.increment_stat('findings_high', 5)
    progress.increment_stat('findings_medium', 10)
    progress.increment_stat('findings_low', 15)
    progress.increment_stat('findings_info', 20)

    # Verify all findings are tracked
    assert progress.stats['findings_critical'] == 2
    assert progress.stats['findings_high'] == 5
    assert progress.stats['findings_medium'] == 10
    assert progress.stats['findings_low'] == 15
    assert progress.stats['findings_info'] == 20

    # Calculate total
    total = sum([
        progress.stats['findings_critical'],
        progress.stats['findings_high'],
        progress.stats['findings_medium'],
        progress.stats['findings_low'],
        progress.stats['findings_info']
    ])
    assert total == 52
