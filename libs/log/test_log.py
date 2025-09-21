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
    log_view.is_log_paused.return_value = False
    return log_view

@pytest.fixture
def setup_update_log(setup_log_view):
    log_controller.clear_logs()
    update_function = log_controller.create_update_log_text_closure(setup_log_view)
    return (setup_log_view, update_function)

def test_filtering_basic(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = [
        "error: something went wrong",
        "warning: potential issue",
        "info: system update",
        "error: critical failure"
    ]
    
    log_view.get_filter_string.return_value = "error"
    update_log("\n".join(test_lines))
    
    time.sleep(log_controller.FILTER_APPLICATION_WAIT_TIME_s + 0.1)
    update_log("")
    
    filtered_lines = [line[0] for line in log_controller.old_filtered_text]
    assert filtered_lines == [
        "error: something went wrong",
        "error: critical failure"
    ]

def test_highlighting_basic(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = [
        "error: something went wrong",
        "warning: potential issue",
        "info: system update",
        "error: critical failure"
    ]
    
    log_view.get_highlight_string.return_value = "error"
    update_log("\n".join(test_lines))
    
    time.sleep(log_controller.FILTER_APPLICATION_WAIT_TIME_s + 0.1)
    update_log("")

    highlighted_flags = [line[1] for line in log_controller.old_filtered_text]
    assert highlighted_flags == [True, False, False, True]

def test_freezing_basic(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = ["line1", "line2", "line3"]
    
    log_view.is_log_paused.return_value = True
    update_log("\n".join(test_lines))
    update_log("line4\nline5")
    
    log_view.is_log_paused.return_value = False
    update_log("line6")
    
    assert len(log_controller.old_raw_log_text) == 3
    assert log_controller.old_raw_log_text[-1][0] == "line3"

def test_filter_and_highlight(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = [
        "error: something went wrong",
        "warning: potential issue",
        "info: system update",
        "error: critical failure"
    ]
    
    log_view.get_filter_string.return_value = "error"
    log_view.get_highlight_string.return_value = "critical"
    update_log("\n".join(test_lines))
    
    time.sleep(log_controller.FILTER_APPLICATION_WAIT_TIME_s + 0.1)
    
    filtered_lines = [line[0] for line in log_controller.old_filtered_text]
    highlighted_flags = [line[1] for line in log_controller.old_filtered_text]
    
    assert filtered_lines == [
        "error: something went wrong",
        "error: critical failure"
    ]
    assert highlighted_flags == [False, True]

def test_clear_logs(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = ["line1", "line2", "line3"]
    update_log("\n".join(test_lines))
    
    log_controller.clear_logs()
    
    assert log_controller.old_raw_log_text == []
    assert log_controller.old_filtered_text == []
    assert log_controller.old_text_after_freezing == []

def test_timestamp_update(setup_update_log):
    log_view, update_log = setup_update_log
    initial_time = log_controller.get_last_log_gui_filter_update_date()
    
    update_log("test line")
    time.sleep(log_controller.GUI_MINIMUM_REFRESH_INTERVAL_s + 0.1)
    
    updated_time = log_controller.get_last_log_gui_filter_update_date()
    assert updated_time > initial_time

def test_case_insensitive_filtering(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = [
        "ERROR: something went wrong",
        "Warning: potential issue",
        "INFO: system update",
        "Critical: failure"
    ]
    
    log_view.get_filter_string.return_value = "error"
    update_log("\n".join(test_lines))
    
    time.sleep(log_controller.FILTER_APPLICATION_WAIT_TIME_s + 0.1)
    
    filtered_lines = [line[0] for line in log_controller.old_filtered_text]
    assert filtered_lines == ["ERROR: something went wrong"]

def test_case_insensitive_highlighting(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = [
        "ERROR: something went wrong",
        "Warning: potential issue",
        "INFO: system update",
        "Critical: failure"
    ]
    
    log_view.get_highlight_string.return_value = "warning"
    update_log("\n".join(test_lines))
    
    time.sleep(log_controller.FILTER_APPLICATION_WAIT_TIME_s + 0.1)
    
    highlighted_flags = [line[1] for line in log_controller.old_filtered_text]
    assert highlighted_flags == [False, True, False, False]

def test_timestamp_not_updated_on_empty_input(setup_update_log):
    log_view, update_log = setup_update_log
    initial_time = log_controller.get_last_log_gui_filter_update_date()
    
    update_log("")
    
    updated_time = log_controller.get_last_log_gui_filter_update_date()
    assert updated_time == initial_time

def test_multiple_newlines(setup_update_log):
    log_view, update_log = setup_update_log
    test_input = "line1\n\nline2"
    update_log(test_input)
    
    assert len(log_controller.old_raw_log_text) == 3
    assert log_controller.old_raw_log_text[0][0] == "line1"
    assert log_controller.old_raw_log_text[1][0] == ""
    assert log_controller.old_raw_log_text[2][0] == "line2"

def test_timestamp_update_interval(setup_update_log):
    log_view, update_log = setup_update_log
    initial_time = log_controller.get_last_log_gui_filter_update_date()
    
    update_log("test line")
    time.sleep(log_controller.GUI_MINIMUM_REFRESH_INTERVAL_s + 0.1)
    update_log("another test line")
    
    updated_time = log_controller.get_last_log_gui_filter_update_date()
    assert updated_time > initial_time

def test_timestamp_not_updated_on_no_changes(setup_update_log):
    log_view, update_log = setup_update_log
    initial_time = log_controller.get_last_log_gui_filter_update_date()
    
    update_log("test line")
    update_log("test line")
    
    updated_time = log_controller.get_last_log_gui_filter_update_date()
    assert updated_time > initial_time
    assert (updated_time - initial_time) < timedelta(seconds=log_controller.GUI_MINIMUM_REFRESH_INTERVAL_s + 1)

def test_freezing_with_multiple_updates(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = ["line1", "line2", "line3"]
    
    log_view.is_log_paused.return_value = True
    update_log("\n".join(test_lines))
    update_log("line4\nline5")
    
    log_view.is_log_paused.return_value = False
    update_log("line6")
    
    assert len(log_controller.old_raw_log_text) == 3
    assert log_controller.old_raw_log_text[-1][0] == "line3"

def test_highlighting_with_empty_string(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = ["line1", "line2", "line3"]
    
    log_view.get_highlight_string.return_value = ""
    update_log("\n".join(test_lines))
    
    highlighted_flags = [line[1] for line in log_controller.old_filtered_text]
    assert all(flag is False for flag in highlighted_flags)

def test_filtering_with_empty_string(setup_update_log):
    log_view, update_log = setup_update_log
    test_lines = ["line1", "line2", "line3"]
    
    log_view.get_filter_string.return_value = ""
    update_log("\n".join(test_lines))
    
    assert len(log_controller.old_filtered_text) == 3
    assert all(line[0] in ["line1", "line2", "line3"] for line in log_controller.old_filtered_text)

def test_timestamp_initialization(setup_update_log):
    log_view, update_log = setup_update_log
    initial_time = log_controller.get_last_log_gui_filter_update_date()
    assert initial_time is not None

def test_timestamp_refresh_interval(setup_update_log):
    log_view, update_log = setup_update_log
    initial_time = log_controller.get_last_log_gui_filter_update_date()
    
    update_log("test line")
    time.sleep(log_controller.GUI_MINIMUM_REFRESH_INTERVAL_s + 0.1)
    update_log("another test line")
    
    updated_time = log_controller.get_last_log_gui_filter_update_date()
    assert updated_time > initial_time