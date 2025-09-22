import datetime
import time
import traceback

# Global variables to track the last log filter and highlight change times
last_filter_change_time = 0
last_highlight_change_time = 0
last_log_gui_filter_update_date = datetime.datetime.now()
old_raw_log_lines = []
old_filtered_lines = []
old_lines_after_pausing = []

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

    def _parse_new_text(new_text):
        pass

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

    def _handle_pausing(raw_log_lines, new_lines, pause_text_state):
        """
        Handle freezing of log text
        """
        nonlocal old_pause_text_state
        global old_lines_after_pausing
        if pause_text_state != old_pause_text_state:
            ### Pause state changed
            if pause_text_state == False:
                # Pause released
                new_lines_f = [tuple(line) for line in raw_log_lines[len(old_lines_after_pausing):]]
                old_lines_after_pausing = raw_log_lines[:len(old_lines_after_pausing)]
                old_pause_text_state = False
            else:
                # Pause pressed
                old_lines_after_pausing = raw_log_lines.copy()
                old_pause_text_state = True
                old_lines_after_pausing = raw_log_lines.copy()
                new_lines_f = new_lines.copy()
        else:
            ### Pause state stays the same
            if pause_text_state == False:
                # log not paused
                old_lines_after_pausing = raw_log_lines.copy()
                new_lines_f = new_lines.copy()
            else:
                # pause ongoing
                old_lines_after_pausing = old_lines_after_pausing.copy()
                new_lines_f = []
        return old_lines_after_pausing, new_lines_f

    def _handle_filtering(old_log_lines, new_log_lines, old_filtered_lines, filter_string):
        """
        Handle filtering of log text
        """
        nonlocal old_filter_string, last_applied_filter_string, filter_input_active
        global last_filter_change_time

        # handle changed filter string
        current_time = time.time()
        if filter_string != old_filter_string:
            old_filter_string = filter_string
            last_filter_change_time = current_time
            log_view.set_highlight_color_for_input_widget("-FILTER-")
            filter_input_active = True

        if (last_applied_filter_string != filter_string) \
            and (current_time - last_filter_change_time > FILTER_APPLICATION_WAIT_TIME_s):
            # change filter string apply timeout expired
            last_applied_filter_string = filter_string
            new_filtered_lines = _apply_text_filter(last_applied_filter_string, old_log_lines + new_log_lines)
            old_filtered_lines = []
            filter_reprint = True
            log_view.set_default_color_for_input_widget("-FILTER-")
            filter_input_active = False
        else:
            if (filter_input_active and
                current_time - last_filter_change_time > FILTER_APPLICATION_WAIT_TIME_s):
                # remove input field coloring even if value didn't change
                log_view.set_default_color_for_input_widget("-FILTER-")
                filter_input_active = False
            if new_log_lines != []:
                new_filtered_lines = _apply_text_filter(last_applied_filter_string, new_log_lines)
                old_filtered_lines = old_filtered_lines.copy()
                filter_reprint = False
            else:
                new_filtered_lines = []
                old_filtered_lines = old_filtered_lines.copy()
                filter_reprint = False

        return new_filtered_lines, old_filtered_lines, filter_reprint

    def _clear_log_text():
        global old_lines_after_pausing
        filtered_text = []
        old_lines_after_pausing = []
        log_view.update_log('', append=False)
        return filtered_text

    def _create_highlighted_text_list(highlight_string, text_to_highlight):
        """
        Get highlighted text list
        """
        if highlight_string == "":
            return [(line[0], False) for line in text_to_highlight]
        else:
            highlighted_list = []
            for line in text_to_highlight:
                line_text = line[0]
                highlighted = highlight_string.lower() in line_text.lower()
                highlighted_list.append((line_text, highlighted))
            return highlighted_list

    def _assemble_changed_highlighted_list(old_log_lines, new_log_lines, applied_highlight_string, highlight_string_changed):
        if old_log_lines == []:
            if new_log_lines == []:
                # no filtered log messages left
                highlighted_list = []
            else:
                # only new filtered log messages
                highlighted_list = _create_highlighted_text_list(applied_highlight_string, new_log_lines)
        else:
            if new_log_lines == []:
                # old filtered messages but no new filtered messages
                if highlight_string_changed == True:
                    highlighted_list = _create_highlighted_text_list(applied_highlight_string, old_log_lines)
                else:
                    highlighted_list = old_log_lines
            else:
                # old filtered messages and new filtered messages
                if highlight_string_changed == True:
                    highlighted_list = _create_highlighted_text_list(applied_highlight_string, old_log_lines + new_log_lines)
                else:
                    highlighted_list =  old_log_lines +_create_highlighted_text_list(applied_highlight_string, new_log_lines)
        return highlighted_list

    def _highlight_text(highlight_string, old_log_lines, new_log_lines):
        """
        Highlight matching text in the log and determine append mode
        """
        # access variables of outer scopes
        nonlocal old_highlight_string, last_applied_highlight_string, highlight_input_active
        global last_highlight_change_time

        # init variables
        highlighted_list = []
        append = False
        highlight_string_changed = True if highlight_string != old_highlight_string else False

        # handle changed highlight string
        current_time = time.time()
        if highlight_string != old_highlight_string:
            # highlight string changed
            old_highlight_string = highlight_string
            last_highlight_change_time = current_time
            log_view.set_highlight_color_for_input_widget("-HIGHLIGHT-")
            highlight_input_active = True

        if (current_time - last_highlight_change_time > FILTER_APPLICATION_WAIT_TIME_s) \
            and (last_applied_highlight_string != highlight_string):
                # change timer expired for new highlight string
                last_applied_highlight_string = highlight_string
                highlighted_list = _assemble_changed_highlighted_list(old_log_lines, new_log_lines, last_applied_highlight_string, True)
                log_view.set_default_color_for_input_widget("-HIGHLIGHT-")
                highlight_input_active = False
                append = False
        elif new_log_lines != []:
            # old highlight string, new lines added, highlight them
            highlighted_list = _assemble_changed_highlighted_list([], new_log_lines, last_applied_highlight_string, False)
            append = True
        else:
            # old highlight string, no change
            highlighted_list = []
            append = True
            if highlight_input_active and (current_time - last_highlight_change_time > FILTER_APPLICATION_WAIT_TIME_s):
                log_view.set_default_color_for_input_widget("-HIGHLIGHT-")
                highlight_input_active = False

        return highlighted_list, append

    def _display_highlighted_text(highlighted_text_to_print, append):
        if (append == False):
            log_view.clear_log()
        log_view.insert_highlighted_text(highlighted_text_to_print)

    def update_log_text(new_text):
        """
        Main function to update log text with filtering and highlighting
        """
        global old_raw_log_lines, old_filtered_lines, last_log_gui_filter_update_date, old_highlighted_text_list

        # add new text lines to raw log
        new_lines = [(line, False) for line in new_text.split('\n') if line]

        # handle pausing
        current_pause_state = log_view.is_log_paused()
        old_lines_after_pausing, new_lines_after_pausing = _handle_pausing(old_raw_log_lines, new_lines, current_pause_state)

        # filter text with filter string
        filter_string = log_view.get_filter_string()
        new_filtered_lines, old_filtered_lines, filter_reprint = _handle_filtering(old_lines_after_pausing, new_lines_after_pausing, old_filtered_lines, filter_string)

        # add highlighting information with highlight string
        highlight_string = log_view.get_highlight_string()
        highlighted_text_list, append = _highlight_text(highlight_string, old_filtered_lines, new_filtered_lines)

        # print highlighted text
        append = False if filter_reprint == True else append
        _display_highlighted_text(highlighted_text_list, append)

        # update state
        old_raw_log_lines = old_raw_log_lines.copy() + new_lines
        old_filtered_lines = old_filtered_lines.copy() + new_filtered_lines
        last_log_gui_filter_update_date = datetime.datetime.now()


    return update_log_text

def get_last_log_gui_filter_update_date():
    return last_log_gui_filter_update_date

def clear_logs():
    global old_raw_log_lines, old_filtered_lines, old_lines_after_pausing
    old_raw_log_lines = []
    old_filtered_lines = []
    old_lines_after_pausing = []
