import tkinter as tk
import FreeSimpleGUI as sg

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

    def insert_colored_text(self, text, color):
        self.log_widget.Widget.tag_configure(color, foreground=color)
        self.log_widget.Widget.insert(tk.END, text, color)
        self.log_widget.Widget.see(tk.END)

    def clear_log(self):
        self.update_log("", append=False)

    def insert_highlighted_text(self, highlighted_text):
        # delete log if needed
        for line_text, highlighted in highlighted_text:
            line_text += '\n'
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

    def get_filter_string(self):
        return self.filter_input_widget.Get()

    def get_highlight_string(self):
        return self.highlight_input_widget.Get()

    def is_log_paused(self):
        return True if (self.pause_button_widget.GetText() == "Unpause") else False

    def display_log_update(self, update_info):
        """
        Display the processed log update
        """
        highlighted_text_list = update_info['highlighted_text_list']
        append = update_info['append']
        if update_info['set_filter_highlight_color']:
            self.set_highlight_color_for_input_widget("-FILTER-")
        if update_info['set_filter_default_color']:
            self.set_default_color_for_input_widget("-FILTER-")
        if update_info['set_highlight_highlight_color']:
            self.set_highlight_color_for_input_widget("-HIGHLIGHT-")
        if update_info['set_highlight_default_color']:
            self.set_default_color_for_input_widget("-HIGHLIGHT-")
        if append == False:
            self.clear_log()
        self.insert_highlighted_text(highlighted_text_list)