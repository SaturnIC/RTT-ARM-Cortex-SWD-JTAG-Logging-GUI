import FreeSimpleGUI as sg
import time
import queue
import threading
import argparse
import libs.log.log_controller as log_controller
from datetime import datetime
from libs.jlink.rtt_handler import RTTHandler
from libs.log.log_view import LogView

# constants
FILTER_APPLICATION_WAIT_TIME_s = 2

class RTTViewer:
    def __init__(self, demo=False):
        # Initialize RTT Handler
        self._rtt_handler = RTTHandler()
        self.supported_mcu_list = self._rtt_handler.get_supported_mcus()
        # GUI setup
        sg.theme('Dark Gray 13')

        # Create layout with new filter, highlight, and pause elements
        self._layout = [
            [sg.Text('Python RTT GUI', size=(30, 1), justification='center')],
            [sg.Column([
                [sg.Text('MCU Chip Name:'),
                 sg.Text("", size=(1, 1)),  # horizontal spacer
                 sg.Combo(self.supported_mcu_list, default_value='STM32F427II',
                          key='-MCU-', size=(20, 1), enable_events=True, auto_size_text=False)]
            ])],
            [sg.Output(size=(80, 20), key='-LOG-', expand_x=True, expand_y=True, font=('Consolas', 10))],
            [sg.Column([
                [sg.Text('Filter:'),
                 sg.Input(key='-FILTER-', size=(20, 1), enable_events=True),
                 sg.Text('Highlight:'),
                 sg.Input(key='-HIGHLIGHT-', size=(20, 1), enable_events=True),
                 sg.Button('Pause', key='-PAUSE-', disabled=False)]
            ])],
            [sg.Column([
                [sg.Button('Connect', key='-CONNECT-'),
                 sg.Button('Disconnect', key='-DISCONNECT-', disabled=True),
                 sg.Button('Clear', key='-CLEAR-'),
                 sg.Text('Status: Disconnected', key='-STATUS-', size=(20, 1))]
            ])]
        ]

        self._window = sg.Window('Python RTT GUI', self._layout, finalize=True, resizable=True)

        # Set minimum size
        self._window.set_min_size((800, 600))

        # Initialize GUI state
        self._update_gui_status(False)
        self.current_mcu = 'STM32F427II'  # Track the currently selected MCU
        self.mcu_filter_string = ''
        self.mcu_list_last_update_time = time.time()

        # Bind the <KeyRelease> event to the Combo widget
        self._window['-MCU-'].Widget.bind("<KeyPress>", lambda event: self._window.write_event_value('-MCU-KEYRELEASE-', event))

        # Create LogView instance
        self.log_view = LogView(
            log_widget=self._window['-LOG-'],
            filter_widget=self._window['-FILTER-'],
            highlight_widget=self._window['-HIGHLIGHT-'],
            pause_button=self._window['-PAUSE-'],
            window=self._window
        )

        # Create log handler
        self.log_handler = log_controller.create_log_processor_and_displayer(self.log_view)
        self.display_queue = queue.Queue()
        self.update_log_text = lambda text: self.display_queue.put(self.log_handler['process'](text))

        self.demo = demo

    def _update_gui_status(self, connected):
        self._window['-STATUS-'].update(
            'Status: Connected' if connected else 'Status: Disconnected'
        )
        self._window['-CONNECT-'].update(disabled=connected)
        self._window['-DISCONNECT-'].update(disabled=not connected)
        #self._window['-PAUSE-'].update(disabled=not connected)

    def _log_processing_thread(self):
        while True:
            try:
                line = self._rtt_handler.log_queue.get(timeout=0.1)
                update_info = self.log_handler['process'](line)
                self.display_queue.put(update_info)
            except queue.Empty:
                pass

    def _process_display_queue(self):
        while not self.display_queue.empty():
            try:
                update_info = self.display_queue.get_nowait()
                self.log_handler['display'](update_info)
            except queue.Empty:
                pass

        # call log gui update at least once per second
        if (datetime.now() - log_controller.get_last_log_gui_filter_update_date()).total_seconds() > log_controller.GUI_MINIMUM_REFRESH_INTERVAL_s:
            update_info = self.log_handler['process']("")
            self.log_handler['display'](update_info)

    def _filter_mcu_list(self, filter_string):
        if (time.time() - self.mcu_list_last_update_time) > FILTER_APPLICATION_WAIT_TIME_s:
            input_text = filter_string.upper()
            filtered = [mcu for mcu in self.supported_mcu_list
                        if input_text in mcu]
            self._window['-MCU-'].update(values=filtered)

    def _demo_loop(self):
        demo_messages = [
            "[INFO] System initialized",
            "[DEBUG] Connecting to peripherals",
            "[WARN] Low battery detected",
            "[ERROR] Failed to read sensor data",
            "[INFO] Processing data",
            "[DEBUG] Update complete",
        ]
        while True:
            for msg in demo_messages:
                self._rtt_handler.log_queue.put(msg + '\n')
                time.sleep(2)
            time.sleep(4)

    def run(self):
        self.update_log_text('')

        # Start log processing thread
        processing_thread = threading.Thread(target=self._log_processing_thread, daemon=True)
        processing_thread.start()

        if self.demo:
            self._update_gui_status(True)
            demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
            demo_thread.start()

        try:
            # GUI event loop
            while True:
                time.sleep(0.001)

                # Check MCU filter
                if self.mcu_filter_string != "":
                    self._filter_mcu_list(self.mcu_filter_string)

                # Check events
                event, values = self._window.read(timeout=100)
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
                        if self._rtt_handler.connect(selected_mcu, print_function=self.update_log_text):
                            self._update_gui_status(True)
                    except Exception as e:
                        sg.popup_error(str(e))
                if event == '-DISCONNECT-':
                    self._rtt_handler.disconnect()
                    self._update_gui_status(False)
                if event == '-CLEAR-':
                    self.log_handler['clear']()
                    log_controller.clear_logs()
                if event in ('-FILTER-', '-HIGHLIGHT-'):
                    # Update the log display when filter or highlight changes
                    update_info = self.log_handler['process']("")
                    self.display_queue.put(update_info)
                if event == '-PAUSE-':
                    # Toggle pause state
                    current_text = self._window['-PAUSE-'].GetText()
                    new_text = 'Unpause' if current_text == 'Pause' else 'Pause'
                    self._window['-PAUSE-'].update(new_text)
                    # Trigger update to show accumulated messages if unpaused
                    update_info = self.log_handler['process']("")
                    self.display_queue.put(update_info)

                # Update log
                self._process_display_queue()
        finally:
            self._rtt_handler.disconnect()
            self._window.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python RTT GUI')
    parser.add_argument('--demo-messages', action='store_true', help='Enable demo mode with sample log messages')
    args = parser.parse_args()

    viewer = RTTViewer(demo=args.demo_messages)
    viewer.run()
