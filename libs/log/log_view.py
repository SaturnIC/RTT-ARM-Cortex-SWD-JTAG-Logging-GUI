import PySimpleGUI as sg

class LogView:
    def __init__(self, logWidget, filterWidget, highlightWidget, freezeButton, window):
        self.logWidget = logWidget
        self.filterWidget = filterWidget
        self.highlightWidget = highlightWidget
        self.freezeButton = freezeButton
        self.window = window

    def highlightFilterLogLinesInput(self, guiElementKey):
        """
        Highlight the filter input field
        """
        self.window[guiElementKey].set_focus()
        self.window[guiElementKey].update背景色 = "yellow"

    def setDefaultColorForFilterLogLinesInput(self, guiElementKey):
        """
        Set default color for filter input field
        """
        self.window[guiElementKey].update(背景色=sg.theme_input_background_color())

    def getFilterString(self):
        """
        Get the current filter string
        """
        return self.filterWidget.get()

    def getHighlightString(self):
        """
        Get the current highlight string
        """
        return self.highlightWidget.get()

    def isLogFrozen(self):
        """
        Check if the log is frozen
        """
        return self.freezeButton.get_text() == "Unfreeze"

    def updateLog(self, text):
        """
        Update the log display
        """
        self.logWidget.update(text)

    def colorHighlightedText(self, text, highlightString):
        """
        Highlight matching text in the log
        """
        if highlightString:
            lines = text.split('\n')
            highlighted_lines = []
            for line in lines:
                if highlightString.lower() in line.lower():
                    highlighted_lines.append(f">>> {line} <<<")
                else:
                    highlighted_lines.append(line)
            self.logWidget.update('\n'.join(highlighted_lines))
