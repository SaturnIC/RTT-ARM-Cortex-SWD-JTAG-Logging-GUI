import time
import tkinter as tk
import FreeSimpleGUI as sg

# Constants
FILTER_APPLICATION_WAIT_TIME_s = 0.5
COLOR_BLUE = 'blue'
COLOR_HIGHLIGHT = 'LightGreen'
COLOR_BLACK = 'black'
COLOR_LIGHT_GREY = "LightGray"

class LogView:
    def __init__(self, log_widget, filter_widget, highlight_widget, pause_button, window):
        self.window = window
        # store widgets
        self.log_widget = log_widget
        self.filter_input_widget = filter_widget
        self.highlight_input_widget = highlight_widget
        self.pause_button_widget = pause_button
        # store default colors
        self.default_background_color = sg.theme_input_background_color()
        self.default_text_color = sg.theme_input_text_color()
        # input fields
        self.last_filter_change_time = 0
        self.last_highlight_change_time = 0
        self.last_filter_input = ""
        self.last_highlight_input = ""
        self.active_highlight_string = ""
        self.active_filter_string = ""
        # configure tags
        self.log_widget.Widget.tag_configure("highlight", background="LightGreen")
        self.log_widget.Widget.tag_configure("default", background="")

    def insert_colored_text(self, text, color):
        self.log_widget.print(text)
        #self.log_widget.Widget.tag_configure(color, foreground=color)
        #self.log_widget.Widget.insert(tk.END, text, color)
        #self.log_widget.Widget.see(tk.END)

    def clear_log(self):
        self.update_log("", append=False)

    def insert_highlighted_text(self, highlighted_text_list):
        # delete log if needed
        for line_text, highlighted in highlighted_text_list:
           #line_text += '\n'
           if highlighted:
               self.insert_colored_text(line_text, COLOR_HIGHLIGHT)
           else:
               self.insert_colored_text(line_text, self.default_text_color)

    def update_log(self, text, append):
        self.log_widget.update(text, append=append)

    def set_highlight_color_for_input_widget(self, gui_element_label):
        self.window[gui_element_label].update(background_color=COLOR_HIGHLIGHT)
        self.window[gui_element_label].update(text_color=COLOR_BLACK)

    def set_default_color_for_input_widget(self, gui_element_label):
        self.window[gui_element_label].update(background_color=self.default_background_color)
        self.window[gui_element_label].update(text_color=self.default_text_color)

    def handle_coloring_of_input_widget(self, input_active, input_label):
        if input_active:
            self.set_highlight_color_for_input_widget(input_label)
        else:
            self.set_default_color_for_input_widget(input_label)
    
    def handle_widget_highlighting(self, filter_input, highlight_input):
        retVal = {}
        current_time = time.time()

        # Handle change of input
        if self.last_filter_input != filter_input:
            self.last_filter_input = filter_input
            self.last_filter_change_time = current_time
            self.handle_coloring_of_input_widget(True, "-FILTER-")
        if self.last_highlight_input != highlight_input:
            self.last_highlight_input = highlight_input
            self.last_highlight_change_time = current_time
            self.handle_coloring_of_input_widget(True, "-HIGHLIGHT-")

        # Handle application of changed input stings
        ## highlight input widget
        if (current_time - self.last_filter_change_time > FILTER_APPLICATION_WAIT_TIME_s) \
           and (self.active_filter_string != self.last_filter_input):
            # change timer expired for new filter string
            self.active_filter_string = self.last_filter_input
            self.handle_coloring_of_input_widget(False, "-FILTER-")
            retVal["filter_string"] = self.active_filter_string
        ## highlight input widget
        if (current_time - self.last_highlight_change_time > FILTER_APPLICATION_WAIT_TIME_s) \
           and (self.active_highlight_string != self.last_highlight_input):
            # change timer expired for new highlight string
            self.active_highlight_string = self.last_highlight_input
            self.handle_coloring_of_input_widget(False, "-HIGHLIGHT-")
            retVal["highlight_string"] = self.active_highlight_string

        return retVal

    def display_log_update(self, update_info):
        """
        Display the processed log update
        """
        # parse input dict
        highlighted_text_list = update_info['highlighted_text_list']
        append = update_info['append']

        # Reset log
        if append == False:
            self.clear_log()

        # Inset log lines in log widget
        self.insert_highlighted_text(highlighted_text_list)