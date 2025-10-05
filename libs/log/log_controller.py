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

GUI_MINIMUM_REFRESH_INTERVAL_s = 0.5

def create_log_processor_and_displayer(log_view):
    """
    Create the log processor and displayer by providing the widgets
    Returns a dict with "process" and 'display' functions
    """
    # Store previous data for comparison
    old_filter_string = ""
    last_applied_filter_string = ""
    old_highlight_string = ""
    last_applied_highlight_string = ""
    old_pause_text_state = False
    active_pause_string = ""
    active_filter_string = ""
    active_highlight_string = ""

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
        nonlocal old_filter_string, last_applied_filter_string
        global last_filter_change_time

        filter_reprint = False
        if last_applied_filter_string != filter_string:
            # change filter string apply timeout expired
            last_applied_filter_string = filter_string
            new_filtered_lines = _apply_text_filter(last_applied_filter_string, old_log_lines + new_log_lines)
            old_filtered_lines = []
            filter_reprint = True
        else:
            # filter string did not change
            if new_log_lines != []:
                new_filtered_lines = _apply_text_filter(last_applied_filter_string, new_log_lines)
                old_filtered_lines = old_filtered_lines.copy()
            else:
                new_filtered_lines = []
                old_filtered_lines = old_filtered_lines.copy()

        return new_filtered_lines, old_filtered_lines, filter_reprint

    def _clear_log_text():
        global old_lines_after_pausing
        filtered_text = []
        old_lines_after_pausing = []
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
        nonlocal old_highlight_string, last_applied_highlight_string
        global last_highlight_change_time

        # init variables
        highlighted_list = []
        append = True

        if last_applied_highlight_string != highlight_string:
            # change timer expired for new highlight string
            last_applied_highlight_string = highlight_string
            highlighted_list = _assemble_changed_highlighted_list(old_log_lines, new_log_lines, last_applied_highlight_string, True)
            append = False
        elif new_log_lines != []:
            # old highlight string, new lines added, highlight them
            highlighted_list = _assemble_changed_highlighted_list([], new_log_lines, last_applied_highlight_string, False)
            append = True
        else:
            # old highlight string, no change
            pass

        return highlighted_list, append

    def process_log_text(new_text = "", filter_string = None, highlight_string = None, pause_string = None):
        """
        Process new log text and return update info
        """
        global old_raw_log_lines, old_filtered_lines, last_log_gui_filter_update_date
        nonlocal active_pause_string, active_filter_string, active_highlight_string

        # parse input parameter
        if filter_string != None:
            active_filter_string = filter_string
        if highlight_string != None:
            active_highlight_string = highlight_string
        if pause_string != None:
            active_pause_string = pause_string

        # add new text lines to raw log
        new_lines = [(line, False) for line in new_text.split('\n') if line]

        # handle pausing
        current_pause_state = True if active_pause_string == "Unpause" else False
        old_lines_after_pausing, new_lines_after_pausing = _handle_pausing(old_raw_log_lines, new_lines, current_pause_state)

        # filter text with filter string
        new_filtered_lines, old_filtered_lines, filter_reprint = _handle_filtering(old_lines_after_pausing, new_lines_after_pausing, old_filtered_lines, active_filter_string)

        # add highlighting information with highlight string
        highlighted_text_list, append = _highlight_text(active_highlight_string, old_filtered_lines, new_filtered_lines)

        # determine final append
        append = False if filter_reprint == True else append

        # update state
        old_raw_log_lines = old_raw_log_lines.copy() + new_lines
        old_filtered_lines = old_filtered_lines.copy() + new_filtered_lines
        last_log_gui_filter_update_date = datetime.datetime.now()

        return {
            "highlighted_text_list": highlighted_text_list,
            "append": append,
        }

    def clear_log():
        global old_raw_log_lines, old_filtered_lines, old_lines_after_pausing
        old_raw_log_lines = []
        old_filtered_lines = []
        old_lines_after_pausing = []
        log_view.update_log("", append=False)

    return {
        "process": process_log_text,
        "clear": clear_log
    }

def get_last_log_gui_filter_update_date():
    return last_log_gui_filter_update_date

def clear_log_data():
    global old_raw_log_lines, old_filtered_lines, old_lines_after_pausing
    old_raw_log_lines = []
    old_filtered_lines = []
    old_lines_after_pausing = []
