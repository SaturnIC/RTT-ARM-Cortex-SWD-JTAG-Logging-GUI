import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
import log_controller
import time


@pytest.fixture
def setup_log_view():
    log_view = Mock()
    log_view.get_filter_string.return_value = ""
    log_view.get_highlight_string.return_value = ""
    log_view.is_log_frozen.return_value = False
    return log_view

@pytest.fixture
def setup_update_log(setup_log_view):
    log_controller.clear_logs()
    update_function = log_controller.create_update_log_text_closure(setup_log_view)
    return (setup_log_view, update_function)


def test_filtering_basic(setup_update_log):
    log_view = setup_update_log[0]
    update_log = setup_update_log[1]

    # Test basic filtering
    test_lines = [
        "error: something went wrong",
        "warning: potential issue",
        "info: system update",
        "error: critical failure"
    ]
    
    # Apply filter for "error"
    log_view.get_filter_string.return_value = "error"

    update_log("\n".join(test_lines))
    time.sleep(0.6)
    update_log("")
    
    # Verify only error lines are shown
    filtered_lines = [line[0] for line in log_controller.old_filtered_text]
    assert filtered_lines[0] == "error: something went wrong"
    assert filtered_lines[1] == "error: critical failure"

def test_highlighting_basic(update_log):
    # Test basic highlighting
    test_lines = [
        "error: something went wrong",
        "warning: potential issue",
        "info: system update",
        "error: critical failure"
    ]
    
    # Apply highlight for "error"
    update_log.log_view.get_highlight_string.return_value = "error"
    update_log("\n".join(test_lines))
    
    # Verify error lines are highlighted
    highlighted_lines = [line[1] for line in update_log.old_filtered_text]
    assert len(highlighted_lines) == 4
    assert highlighted_lines[0]  # First line should be highlighted
    assert highlighted_lines[3]  # Last line should be highlighted
    assert not highlighted_lines[1]  # Middle lines should not be highlighted
    assert not highlighted_lines[2]

def test_freezing_basic(update_log):
    # Test freezing functionality
    test_lines = ["line1", "line2", "line3"]
    
    # Freeze the log
    update_log.log_view.is_log_frozen.return_value = True
    update_log("\n".join(test_lines))
    
    # Add more lines while frozen
    update_log("line4\nline5")
    
    # Thaw the log
    update_log.log_view.is_log_frozen.return_value = False
    update_log("line6")
    
    # Verify only initial lines are present
    assert len(update_log.old_raw_log_text) == 3
    assert update_log.old_raw_log_text[-1][0] == "line3"

def test_filter_and_highlight(update_log):
    # Test combined filtering and highlighting
    test_lines = [
        "error: something went wrong",
        "warning: potential issue",
        "info: system update",
        "error: critical failure"
    ]
    
    # Set filter and highlight
    update_log.log_view.get_filter_string.return_value = "error"
    update_log.log_view.get_highlight_string.return_value = "critical"
    update_log("\n".join(test_lines))
    
    # Verify only error lines are shown, and critical line is highlighted
    filtered_lines = [line[0] for line in update_log.old_filtered_text]
    highlighted_flags = [line[1] for line in update_log.old_filtered_text]
    
    assert "error: something went wrong" in filtered_lines
    assert "error: critical failure" in filtered_lines
    assert len(highlighted_flags) == 2
    assert not highlighted_flags[0]
    assert highlighted_flags[1]

def test_clear_logs(update_log):
    # Test clearing logs
    test_lines = ["line1", "line2", "line3"]
    update_log("\n".join(test_lines))
    
    # Clear logs
    log_controller.clear_logs()
    
    # Verify all logs are cleared
    assert update_log.old_raw_log_text == []
    assert update_log.old_filtered_text == []
    assert update_log.old_text_after_freezing == []

def test_timestamp_update(update_log):
    # Test timestamp updates
    initial_time = get_last_log_gui_filter_update_date()
    
    # Update log
    update_log("test line")
    
    # Verify timestamp updated
    updated_time = get_last_log_gui_filter_update_date()
    assert updated_time > initial_time

def test_case_insensitive_filtering(update_log):
    # Test case-insensitive filtering
    test_lines = [
        "ERROR: something went wrong",
        "Warning: potential issue",
        "INFO: system update",
        "Critical: failure"
    ]
    
    # Apply lowercase filter
    update_log.log_view.get_filter_string.return_value = "error"
    update_log("\n".join(test_lines))
    
    # Verify case-insensitive filtering
    filtered_lines = [line[0] for line in update_log.old_filtered_text]
    assert "ERROR: something went wrong" in filtered_lines
    assert len(filtered_lines) == 1

def test_case_insensitive_highlighting(update_log):
    # Test case-insensitive highlighting
    test_lines = [
        "ERROR: something went wrong",
        "Warning: potential issue",
        "INFO: system update",
        "Critical: failure"
    ]
    
    # Apply lowercase highlight
    update_log.log_view.get_highlight_string.return_value = "warning"
    update_log("\n".join(test_lines))
    
    # Verify case-insensitive highlighting
    highlighted_flags = [line[1] for line in update_log.old_filtered_text]
    assert highlighted_flags[1]  # "Warning" should be highlighted

def test_timestamp_not_updated_on_empty_input(update_log):
    # Test timestamp not updated on empty input
    initial_time = get_last_log_gui_filter_update_date()
    
    # Update with empty string
    update_log("")
    
    # Verify timestamp not updated
    updated_time = get_last_log_gui_filter_update_date()
    assert updated_time == initial_time

def test_multiple_newlines(update_log):
    # Test handling of multiple newlines
    test_input = "line1\n\nline2"
    
    # Update log
    update_log(test_input)
    
    # Verify lines are correctly split
    assert len(update_log.old_raw_log_text) == 3
    assert update_log.old_raw_log_text[0][0] == "line1"
    assert update_log.old_raw_log_text[1][0] == ""
    assert update_log.old_raw_log_text[2][0] == "line2"

def test_timestamp_update_interval(update_log):
    # Test timestamp update interval
    global last_log_gui_filter_update_date
    initial_time = last_log_gui_filter_update_date
    
    # Update log
    update_log("test line")
    
    # Verify timestamp updated
    updated_time = get_last_log_gui_filter_update_date()
    assert updated_time > initial_time

def test_timestamp_not_updated_on_no_changes(update_log):
    # Test timestamp not updated on no changes
    initial_time = get_last_log_gui_filter_update_date()
    
    # Update log with same content
    update_log("test line")
    update_log("test line")
    
    # Verify timestamp only updated once
    updated_time = get_last_log_gui_filter_update_date()
    assert updated_time > initial_time
    assert (updated_time - initial_time) < timedelta(seconds=GUI_MINIMUM_REFRESH_INTERVAL_s + 1)

def test_freezing_with_multiple_updates(update_log):
    # Test freezing with multiple updates
    test_lines = ["line1", "line2", "line3"]
    
    # Freeze the log
    update_log.log_view.is_log_frozen.return_value = True
    update_log("\n".join(test_lines))
    
    # Add more lines while frozen
    update_log("line4\nline5")
    
    # Thaw the log
    update_log.log_view.is_log_frozen.return_value = False
    update_log("line6")
    
    # Verify only initial lines are present
    assert len(update_log.old_raw_log_text) == 3
    assert update_log.old_raw_log_text[-1][0] == "line3"

def test_highlighting_with_empty_string(update_log):
    # Test highlighting with empty string
    test_lines = ["line1", "line2", "line3"]
    
    # Set empty highlight string
    update_log.log_view.get_highlight_string.return_value = ""
    update_log("\n".join(test_lines))
    
    # Verify no highlighting applied
    highlighted_flags = [line[1] for line in update_log.old_filtered_text]
    assert all(flag is False for flag in highlighted_flags)

def test_filtering_with_empty_string(update_log):
    # Test filtering with empty string
    test_lines = ["line1", "line2", "line3"]
    
    # Set empty filter string
    update_log.log_view.get_filter_string.return_value = ""
    update_log("\n".join(test_lines))
    
    # Verify all lines are shown
    assert len(update_log.old_filtered_text) == 3
    assert all(line[0] in ["line1", "line2", "line3"] for line in update_log.old_filtered_text)

def test_timestamp_initialization(update_log):
    # Test initial timestamp
    initial_time = get_last_log_gui_filter_update_date()
    assert initial_time is not None

def test_timestamp_refresh_interval(update_log):
    # Test timestamp refresh interval
    global last_log_gui_filter_update_date
    initial_time = last_log_gui_filter_update_date
    
    # Update log
    update_log("test line")
    
    # Verify timestamp updated after interval
    time.sleep(GUI_MINIMUM_REFRESH_INTERVAL_s + 1)
    update_log("another test line")
    updated_time = get_last_log_gui_filter_update_date()
    assert updated_time > initial_time
    test_lines = [
        "ERROR: something went wrong",
        "Warning: potential issue",
        "INFO: system update",
        "Critical: failure"
    ]
    
    # Apply lowercase filter
    update_log.log_view.get_filter_string.return_value = "error"
    update_log("\n".join(test_lines))
    
    # Verify case-insensitive filtering
    filtered_lines = [line[0] for line in update_log.old_filtered_text]
    assert "ERROR: something went wrong" in filtered_lines
    assert len(filtered_lines) == 1
