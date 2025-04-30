import tkinter as tk
import FreeSimpleGUI as sg

COLOR_BLUE = 'blue'
COLOR_HIGHLIGHT = 'LightGreen'
COLOR_BLACK = 'black'
COLOR_LIGHT_GREY = "LightGray"

"""
Create the update log text closure by providing the widgets
"""
class LogView:
    def __init__(self, log_widget, filter_widget, highlight_widget, pause_button, window):
        self.window = window
        # store widgets
        self.log_widget = log_widget
        self.filter_input_widget = filter_widget
        self.highlight_input_widget = highlight_widget
        self.pause_button_widget = pause_button
        # store default colors
        self.default_background_color=sg.theme_input_background_color()
        self.default_text_color=sg.theme_input_text_color()

    # function to insert colored text
    def insert_colored_text(self, text, color):
        self.log_widget.Widget.tag_configure(color, foreground=color)
        self.log_widget.Widget.insert(tk.END, text, color)
        self.log_widget.Widget.see(tk.END)

    def color_highlighted_text(self, text, highlight_string, append):
        # delete log if needed
        if (append == False):
            self.update_log("", append=False)
        for line in text.splitlines():
            line += '\n'
            if highlight_string.lower() in line.lower():
                self.insert_colored_text(line, COLOR_HIGHLIGHT)
            else:
                self.insert_colored_text(line, self.default_text_color)

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

    def is_log_frozen(self):
        return True if (self.pause_button_widget.GetText()=="Unpause") else False