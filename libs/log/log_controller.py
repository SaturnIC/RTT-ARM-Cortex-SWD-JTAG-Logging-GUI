import datetime
import time
import traceback

# Global variables to track the last log filter and highlight change times
last_filter_change_time = 0
last_highlight_change_time = 0
last_log_gui_filter_update_date = datetime.datetime.now()
old_raw_log_text = []
old_filtered_text = []
old_text_after_freezing = []

# Constants
FILTER_APPLICATION_WAIT_TIME_s = 0.5
GUI_MINIMUM_REFRESH_INTERVAL_s = 0.5

def create_update_log_text_closure(log_view):
    """
    Create the update log text closure by providing the widgets
    """
    # Store previous data for comparison
    old_filter_string = ""
    last_applied_filter_string = ""
    filter_input_active = False
    old_highlight_string = ""
    last_applied_highlight_string = ""
    highlight_input_active = False
    old_pause_text_state = False

    def _apply_text_filter(filter_str, unfiltered_content):
        """
        Text log filter function
        """
        if not filter_str:
            return unfiltered_content.copy()

        filtered_lines = []
        filter_str_lower = filter_str.lower()
        for line_tuple in unfiltered_content:
            line = line_tuple[0]
            if filter_str_lower in line.lower():
                filtered_lines.append(line_tuple)
        return filtered_lines

    def _handle_freezing(raw_log_text, new_text, pause_text_state):
        """
        Handle freezing of log text
        """
        nonlocal old_pause_text_state
        global old_text_after_freezing

        if pause_text_state != old_pause_text_state:
            ### Pause state changed
            if not pause_text_state:
                # Pause released
                raw_text_after_freezing = raw_log_text.copy()
                new_text_f = [tuple(line) for line in raw_log_text[len(old_text_after_freezing):]]
                old_pause_text_state = False
            else:
                # Pause pressed
                raw_text_after_freezing = raw_log_text.copy()
                old_pause_text_state = True
                old_text_after_freezing = raw_log_text.copy()
                new_text_f = new_text.copy()
        else:
            ### Pause state stays the same
            if not pause_text_state:
                # Text not frozen
                raw_text_after_freezing = raw_log_text.copy()
                new_text_f = new_text.copy()
            else:
                # Text frozen
                raw_text_after_freezing = old_text_after_freezing.copy()
                new_text_f = []

        return raw_text_after_freezing, new_text_f

    def _handle_filtering(all_text, new_text, old_filtered_text, filter_string):
        """
        Handle filtering of log text
        """
        nonlocal old_filter_string, last_applied_filter_string, filter_input_active
        global last_filter_change_time

        if not filter_string:
            filtered_text = all_text.copy()
            if old_filter_string:
                old_filter_string = ""
                last_applied_filter_string = ""
                log_view.set_default_color_for_input_widget("-FILTER-")
        else:
            current_time = time.time()
            if filter_string != old_filter_string:
                old_filter_string = filter_string
                last_filter_change_time = current_time
                log_view.set_highlight_color_for_input_widget("-FILTER-")
                filter_input_active = True

            if (last_applied_filter_string != filter_string) and \
               (current_time - last_filter_change_time > FILTER_APPLICATION_WAIT_TIME_s):
                last_applied_filter_string = filter_string
                filtered_text = _apply_text_filter(last_applied_filter_string, all_text)
                log_view.set_default_color_for_input_widget("-FILTER-")
                filter_input_active = False
            else:
                if (filter_input_active and
                    current_time - last_filter_change_time > FILTER_APPLICATION_WAIT_TIME_s):
                    log_view.set_default_color_for_input_widget("-FILTER-")
                    filter_input_active = False
                if new_text:
                    filtered_text = old_filtered_text + _apply_text_filter(last_applied_filter_string, new_text)
                else:
                    filtered_text = old_filtered_text.copy()

        return filtered_text

    def _clear_log_text():
        global old_text_after_freezing
        filtered_text = []
        old_text_after_freezing = []
        log_view.update_log('', append=False)
        return filtered_text

    def _highlight_text(highlight_string, filtered_text):
        """
        Highlight matching text in the log
        """
        nonlocal old_highlight_string
        global old_filtered_text, last_applied_highlight_string, highlight_input_active, last_highlight_change_time

        if not highlight_string:
            if old_highlight_string:
                log_view.update_log("", append=False)
                old_filtered_text = filtered_text.copy()
                last_applied_highlight_string = ""
            return

        current_time = time.time()
        if highlight_string != old_highlight_string:
            last_highlight_change_time = current_time
            log_view.set_highlight_color_for_input_widget("-HIGHLIGHT-")
            highlight_input_active = True

        if ((current_time - last_highlight_change_time > FILTER_APPLICATION_WAIT_TIME_s) and
            (last_applied_highlight_string != highlight_string)):
            last_applied_highlight_string = highlight_string
            highlighted_text = []
            for line in filtered_text:
                line_text = line[0]
                if highlight_string.lower() in line_text.lower():
                    highlighted_text.append((line_text, True))
                else:
                    highlighted_text.append((line_text, False))
            log_view.color_highlighted_text(highlighted_text, append=False)
            log_view.set_default_color_for_input_widget("-HIGHLIGHT-")
            highlight_input_active = False
            old_filtered_text = highlighted_text.copy()
        else:
            if len(filtered_text) > len(old_filtered_text):
                diff = len(filtered_text) - len(old_filtered_text)
                new_lines = filtered_text[-diff:]
                highlighted_lines = []
                for line in new_lines:
                    line_text = line[0]
                    if highlight_string.lower() in line_text.lower():
                        highlighted_lines.append((line_text, True))
                    else:
                        highlighted_lines.append((line_text, False))
                log_view.color_highlighted_text(highlighted_lines, append=True)
            else:
                highlighted_text = []
                for line in filtered_text:
                    line_text = line[0]
                    if highlight_string.lower() in line_text.lower():
                        highlighted_text.append((line_text, True))
                    else:
                        highlighted_text.append((line_text, False))
                log_view.color_highlighted_text(highlighted_text, append=False)
                old_filtered_text = highlighted_text.copy()

        old_highlight_string = highlight_string

    def update_log_text(new_text):
        """
        Main function to update log text with filtering and highlighting
        """
        global old_raw_log_text, old_filtered_text, last_log_gui_filter_update_date

        current_pause_state = log_view.is_log_frozen()
        new_lines = [(line, False) for line in new_text.split('\n') if line]
        raw_log_text = old_raw_log_text + new_lines
        raw_text_after_freezing, new_text = _handle_freezing(raw_log_text, new_lines, current_pause_state)
        filter_string = log_view.get_filter_string()
        filtered_text = _handle_filtering(raw_text_after_freezing, new_text, old_filtered_text, filter_string)

        highlight_string = log_view.get_highlight_string()
        if highlight_string:
            _highlight_text(highlight_string, filtered_text)
        else:
            log_view.set_default_color_for_input_widget("-HIGHLIGHT-")
            log_view.update_log(filtered_text, append=False)

        old_raw_log_text = raw_text_after_freezing.copy()
        old_filtered_text = filtered_text.copy()
        last_log_gui_filter_update_date = datetime.datetime.now()

    return update_log_text

def get_last_log_gui_filter_update_date():
    return last_log_gui_filter_update_date

def clear_logs():
    global old_raw_log_text, old_filtered_text, old_text_after_freezing
    old_raw_log_text = []
    old_filtered_text = []
    old_text_after_freezing = []