import PySimpleGUI as sg
import time
import queue
import time
from libs.jlink.rtt_handler import RTTHandler
from libs.log.log_controller import createUpdateLogTextClosure
from libs.log.log_view import LogView

# constants
FILTER_APPLICATION_WAIT_TIME_s = 1

# Colors
COLOR_DARK_GREY = '#181818'
COLOR_LIGHT_GREY = '#424242'
COLOR_VLIGHT_GREY = '#929292'
COLOR_BLACK = '#000000'
COLOR_WHITE = '#FFFFFF'
COLOR_YELLOW = '#FFF703'
COLOR_RED = 'orangered'
COLOR_BLUE = 'dodgerblue'
COLOR_GREEN = 'springgreen'
COLOR_HIGHLIGHT = 'aquamarine'
COLOR_BACKGROUND = 'black'

class RTTViewer:
    def __init__(self):
        # Initialize RTT Handler
        self._rtt_handler = RTTHandler()
        self.supported_mcu_list = self._rtt_handler.get_supported_mcus()
        # GUI setup
        sg.theme('Dark Gray 13')

        # Create layout with new filter, highlight, and freeze elements
        self._layout = [
            [sg.Text('Segger RTT GUI', size=(30, 1), justification='center')],
            [sg.Column([
                [sg.Text('MCU Chip Name:'),
                 sg.Combo(self.supported_mcu_list, default_value='STM32F427II',
                          key='-MCU-', size=(20, 1), enable_events=True)]
            ])],
            [sg.Output(size=(80, 20), key='-LOG-', font=('Consolas', 10))],
            [sg.Column([
                [sg.Text('Filter:'),
                 sg.Input(key='-FILTER-', size=(20, 1)),
                 sg.Text('Highlight:'),
                 sg.Input(key='-HIGHLIGHT-', size=(20, 1)),
                 sg.Button('Freeze', key='-FREEZE-', disabled=False)]
            ])],
            [sg.Column([
                [sg.Button('Connect', key='-CONNECT-'),
                 sg.Button('Disconnect', key='-DISCONNECT-', disabled=True),
                 sg.Button('Clear', key='-CLEAR-'),
                 sg.Text('Status: Disconnected', key='-STATUS-', size=(20, 1))]
            ])]
        ]

        self._window = sg.Window('Python RTT GUI', self._layout, finalize=True)

        # Initialize GUI state
        self._update_gui_status(False)
        self.current_mcu = 'STM32F427II'  # Track the currently selected MCU
        self.mcu_filter_string = ''
        self.mcu_list_last_update_time = time.time()

        # Bind the <KeyRelease> event to the Combo widget
        self._window['-MCU-'].Widget.bind("<KeyRelease>", lambda event: self._window.write_event_value('-MCU-KEYRELEASE-', event))

        # Create LogView instance
        self.log_view = LogView(
            logWidget=self._window['-LOG-'],
            filterWidget=self._window['-FILTER-'],
            highlightWidget=self._window['-HIGHLIGHT-'],
            freezeButton=self._window['-FREEZE-'],
            window=self._window
        )

        # Create update closure
        self.update_log_text = createUpdateLogTextClosure(self.log_view)

    def _update_gui_status(self, connected):
        self._window['-STATUS-'].update(
            'Status: Connected' if connected else 'Status: Disconnected'
        )
        self._window['-CONNECT-'].update(disabled=connected)
        self._window['-DISCONNECT-'].update(disabled=not connected)
        self._window['-FREEZE-'].update(disabled=not connected)

    def _process_log_queue(self):
        while not self._rtt_handler.log_queue.empty():
            try:
                data = self._rtt_handler.log_queue.get_nowait()
                # Use the update closure to process and display data
                self.update_log_text(data)
            except queue.Empty:
                pass

    def _filter_mcu_list(self, filter_string):
        if (time.time() - self.mcu_list_last_update_time) > FILTER_APPLICATION_WAIT_TIME_s:
            input_text = filter_string.lower()
            filtered = [mcu for mcu in self.supported_mcu_list
                        if input_text in mcu.lower()]
            self._window['-MCU-'].update(values=filtered)

    def run(self):
        try:
            while True:
                time.sleep(0.001)
                # Check MCU filter
                if self.mcu_filter_string != "":
                    if (time.time() - self.mcu_list_last_update_time) > FILTER_APPLICATION_WAIT_TIME_s:
                        self._filter_mcu_list(self.mcu_filter_string)
                # Check events
                event, values = self._window.read(timeout=100)
                if event == '__TIMEOUT__':
                    continue
                if event == sg.WIN_CLOSED:
                    break
                if event == '-MCU-':
                    self.current_mcu = values['-MCU-']
                    self.mcu_filter_string = ""
                if event == '-MCU-KEYRELEASE-':
                    self.mcu_filter_string = values['-MCU-']
                    self.mcu_list_last_update_time = time.time()
                if event == '-CONNECT-':
                    try:
                        selected_mcu = self._window['-MCU-'].get()
                        if self._rtt_handler.connect(selected_mcu, print_function=self._append_to_log):
                            self._update_gui_status(True)
                    except Exception as e:
                        sg.popup_error(str(e))
                if event == '-DISCONNECT-':
                    self._rtt_handler.disconnect()
                    self._update_gui_status(False)
                if event == '-CLEAR-':
                    self._window['-LOG-'].update('')
                if event in ('-FILTER-', '-HIGHLIGHT-'):
                    # Update the log display when filter or highlight changes
                    if self._window['-FREEZE-'].GetText()=="Unfreeze":
                        self._window['-FREEZE-'].update("Freeze", button_color = (COLOR_WHITE, COLOR_LIGHT_GREY))
                    else:
                        self._window['-FREEZE-'].update("Unfreeze", button_color = (COLOR_WHITE, COLOR_BLUE))
                if event == '-FREEZE-':
                    # Toggle freeze state
                    current_text = self._window['-FREEZE-'].GetText()
                    new_text = 'Unfreeze' if current_text == 'Freeze' else 'Freeze'
                    self._window['-FREEZE-'].update(new_text)
                # Update log
                self._process_log_queue()
        finally:
            self._rtt_handler.disconnect()
            self._window.close()

    def _append_to_log(self, message):
        self._window['-LOG-'].update(message, append=True)

if __name__ == "__main__":
    viewer = RTTViewer()
    viewer.run()