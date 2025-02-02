import datetime
import time
import traceback

# Global variables to track the last log filter and highlight change times
last_filter_change_time = 0
last_highlight_change_time = 0
last_log_gui_filter_update_date = datetime.datetime.now()
old_raw_log_text = ""
old_filtered_text = ""
old_text_after_freezing = ""

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
        filtered_lines = ""
        if filter_str:
            for line in unfiltered_content.split('\n'):
                if filter_str.lower() in line.lower():
                    filtered_lines += line + '\n'
        else:
            filtered_lines = unfiltered_content
        return filtered_lines

    def _handle_freezing(raw_log_text, new_text, pause_text_state):
        """
        Handle freezing of log text
        """
        global old_text_after_freezing
        nonlocal old_pause_text_state
        if pause_text_state != old_pause_text_state:
            ### Pause state changed
            if not pause_text_state:
                # Pause released
                raw_text_after_freezing = raw_log_text
                new_text_f = raw_text_after_freezing[len(old_text_after_freezing):]
                old_pause_text_state = False
            else:
                # Pause pressed
                raw_text_after_freezing = raw_log_text
                old_pause_text_state = True
                old_text_after_freezing = raw_log_text
                new_text_f = new_text
        else:
            ### Pause state stays the same
            if not pause_text_state:
                # Text not frozen
                raw_text_after_freezing = raw_log_text
                new_text_f = new_text
            else:
                # Text frozen
                raw_text_after_freezing = old_text_after_freezing
                new_text_f = ""
        return raw_text_after_freezing, new_text_f

    def _handle_filtering(all_text, new_text, old_filtered_text, filter_string):
        """
        Handle filtering of log text
        """
        nonlocal old_filter_string
        nonlocal last_applied_filter_string
        nonlocal filter_input_active
        global last_filter_change_time
        if filter_string == "":
            filtered_text = all_text
            if old_filter_string != "":
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
                    filtered_text = old_filtered_text
        return filtered_text

    def _clear_log_text():
        global old_text_after_freezing
        filtered_text = ""
        old_text_after_freezing = ""
        log_view.update_log('', append=False)
        return filtered_text

    def _highlight_text(highlight_string, filtered_text):
        """
        Highlight matching text in the log
        """
        nonlocal old_highlight_string
        global old_filtered_text
        nonlocal last_applied_highlight_string
        nonlocal highlight_input_active
        global last_highlight_change_time
        if filtered_text == "":
            log_view.update_log("", append=False)
            old_filtered_text = filtered_text
        else:
            # filtered text is not empty
            if highlight_string == "":
                # highlight string is empty
                if highlight_string == old_highlight_string:
                    # highlight string didn't change
                    if filtered_text != old_filtered_text:
                        # highlight strings
                        if len(filtered_text) > len(old_filtered_text):
                            # new text text is larger than old filtered text
                            if filtered_text[:len(old_filtered_text)] == old_filtered_text:
                                # new old text is the old filtered text and some new text -> append only new text
                                new_text = filtered_text[len(old_filtered_text):]
                                log_view.update_log(new_text, append=True)
                            else:
                                # new text is not an extension of old text -> draw everything again
                                log_view.update_log(filtered_text, append=False)
                        elif len(filtered_text) == len(old_filtered_text):
                            # nothing to do
                            pass
                        else:
                            # text is different from old text -> draw everything again
                            log_view.update_log(filtered_text, append=False)
                else:
                    # new empty highlight text -> draw all text again, disable color in input text field
                    log_view.update_log(filtered_text, append=False)
                    old_filtered_text = filtered_text
                    last_applied_highlight_string = ""
            else:
                # highlight string is not empty
                current_time = time.time()

                # handle highlight timeout
                if highlight_string != old_highlight_string:
                    # filter string changed -> update filter application time + color highlight input active
                    last_highlight_change_time = current_time
                    log_view.set_highlight_color_for_input_widget("-HIGHLIGHT-")
                    highlight_input_active = True
                # use new highlight sting after timeout expired
                if ((current_time - last_highlight_change_time > FILTER_APPLICATION_WAIT_TIME_s)
                    and (last_applied_highlight_string != highlight_string)):
                    # highlight string changed and change wait timeout expired -> redraw complete log + disable active color for highlight input
                    last_applied_highlight_string = highlight_string
                    log_view.color_highlighted_text(filtered_text, last_applied_highlight_string, append=False)
                    log_view.set_default_color_for_input_widget("-HIGHLIGHT-")
                    highlight_input_active = False
                else:
                    # highlight strings
                    if len(filtered_text) > len(old_filtered_text):
                        # new text text is larger than old filtered text
                        if filtered_text[:len(old_filtered_text)] == old_filtered_text:
                            # new filtered text is the old filtered text and some new filtered text -> append only new filtered text
                            new_text = filtered_text[len(old_filtered_text):]
                            log_view.color_highlighted_text(new_text, last_applied_highlight_string, append=True)
                        else:
                            # new filtered text is not an extension of old filtered text -> draw everything again
                            log_view.color_highlighted_text(filtered_text, last_applied_highlight_string, append=False)
                    elif len(filtered_text) == len(old_filtered_text):
                        # nothing to do
                        pass
                    else:
                        # filtered text is different from old filtered text -> draw everything again
                        log_view.color_highlighted_text(filtered_text, last_applied_highlight_string, append=False)
                old_filtered_text = filtered_text
        old_highlight_string = highlight_string

    def update_log_text(new_text):
        """
        Main function to update log text with filtering and highlighting
        """
        global old_raw_log_text
        global old_filtered_text
        global last_log_gui_filter_update_date
        current_pause_state = log_view.is_log_frozen()
        raw_log_text = old_raw_log_text + new_text
        raw_text_after_freezing, new_text = _handle_freezing(raw_log_text, new_text, current_pause_state)
        filtered_text = _handle_filtering(raw_text_after_freezing, new_text, old_filtered_text, log_view.get_filter_string())
        if log_view.get_highlight_string() != "":
            # highlight string empty
            _highlight_text(log_view.get_highlight_string(), filtered_text)
        else:
            # highlight string empty
            log_view.set_default_color_for_input_widget("-HIGHLIGHT-")
            log_view.update_log(filtered_text, append=False)
        old_raw_log_text = raw_text_after_freezing
        old_filtered_text = filtered_text
        last_log_gui_filter_update_date = datetime.datetime.now()

    return update_log_text

def get_last_log_gui_filter_update_date():
    return last_log_gui_filter_update_date

def clear_logs():
    global old_raw_log_text
    global old_filtered_text
    global old_text_after_freezing

    old_raw_log_text = ""
    old_filtered_text = ""
    old_text_after_freezing = ""