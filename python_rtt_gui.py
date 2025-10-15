import FreeSimpleGUI as sg
import time
import queue
import threading
import argparse
import libs.log.log_controller as log_controller
from datetime import datetime
from libs.jlink.rtt_handler import RTTHandler
from libs.jlink.demo_rtt_handler import DemoRTTHandler
from libs.jlink.rtt_handler_interface import RTTHandlerInterface
from libs.log.log_view import LogView

# constants
LOG_UPDATE_TIME_INTERVAL_ms = 100


class RTTViewer:
    def __init__(self, demo=False):
        self.filter_input_string = ""
        self.highlight_input_string = ""
        self.last_processed_time = time.time()
        self.log_update_time_interval_s = LOG_UPDATE_TIME_INTERVAL_ms / 1000.0

        # Create queues
        self.log_processing_input_queue = queue.Queue()
        self.display_output_queue = queue.Queue()

        # Initialize RTT Handler
        if demo:
            self._rtt_handler = DemoRTTHandler(self.log_processing_input_queue)
        else:
            self._rtt_handler = RTTHandler(self.log_processing_input_queue)
        self.supported_mcu_list = self._rtt_handler.get_supported_mcus()
        # GUI setup
        sg.theme('Dark Gray 13')

        # Create layout with new filter, highlight, and pause elements
        self._layout = [
            [sg.Text('ARM Cortex RTT GUI', size=(20, 1), justification='center')],
            [sg.Frame('Configuration', [
                [sg.Text('MCU Chip Name:', size=(14, 1)),
                sg.Text("", size=(1, 1)),  # horizontal spacer
                sg.Combo(self.supported_mcu_list, default_value='DEMO_MCU' if demo else 'STM32F427II',
                        key='-MCU-', size=(20, 1), enable_events=True, auto_size_text=False)],
                [sg.Text('Interface:', size=(14, 1)),
                sg.Text("", size=(1, 1)),  # horizontal spacer
                sg.Combo(['SWD', 'JTAG'], default_value='SWD',
                        key='-INTERFACE-', size=(10, 1), auto_size_text=False)],
                ], pad=((10,30),(10,10))),
            sg.Frame('Connection', [
                [sg.Button('Connect', key='-CONNECT-'),
                sg.Button('Disconnect', key='-DISCONNECT-', disabled=True)],
                [sg.Text('Status: Disconnected', key='-STATUS-', size=(20, 1))]
                ], pad=((20,10),(10,10)))
            ],
            [sg.Frame('Log', [
                [sg.Multiline(size=(80, 20), key='-LOG-', expand_x=True, expand_y=True, font=('Consolas', 10))],
                [sg.Column([
                    [sg.Text('Filter:'),
                     sg.Input(key='-FILTER-', size=(20, 1), enable_events=True),
                     sg.Text('Highlight:'),
                     sg.Input(key='-HIGHLIGHT-', size=(20, 1), enable_events=True),
                     sg.Button('Pause', key='-PAUSE-', disabled=False),
                     sg.Button('Clear', key='-CLEAR-')]
                ])]
            ], expand_x=True, expand_y=True, pad=((10,10),(10,20)))]
        ]

        self._window = sg.Window('ARM Cortex RTT GUI', self._layout, finalize=True, resizable=True)

        # Set minimum size
        self._window.set_min_size((800, 600))

        # Initialize GUI state
        self._update_gui_status(False)

        self.mcu_filter_string = ''
        self.last_mcu_filter_string = ""
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
                # Get element from input queue
                log_input = self.log_processing_input_queue.get(timeout=0.1)

                # Parse log processing item
                line = log_input["line"] if "line" in log_input else ""
                filter_string = log_input["filter_string"] if "filter_string" in log_input else None
                highlight_string = log_input["highlight_string"] if "highlight_string" in log_input else None
                pause_string = log_input["pause_string"] if "pause_string" in log_input else None

                # Invoke processing
                update_info = self.log_handler["process"](line, filter_string, highlight_string, pause_string)

                # Add processing result to output queue
                self.display_output_queue.put(update_info)
            except queue.Empty:
                pass
            time.sleep(0.01)

    def _process_display_output_queue(self):
        count = 0
        max_per_call = 20  # Limit to 100 lines per GUI update to prevent overload
        highlighted_log_lines = []
        update_info = []
        while not self.display_output_queue.empty() and count < max_per_call:
            try:
                update_info = self.display_output_queue.get_nowait()
                highlighted_log_lines += update_info['highlighted_text_list']
                count += 1
                if update_info["append"] == False:
                    break
            except queue.Empty:
                break
        if update_info != []:
            # print processed lines
            #highlighted_log_lines.append((f"count on print: {count}", False))
            update_info['highlighted_text_list'] = highlighted_log_lines
            self.log_view.display_log_update(update_info)
        #else:
        #    # call log gui update at least once per second
        #    if (datetime.now() - log_controller.get_last_log_gui_filter_update_date()).total_seconds() > log_controller.GUI_MINIMUM_REFRESH_INTERVAL_s:
        #        update_info = self.log_handler["process"]("")
        #        self.log_view.display_log_update(update_info)

    def _filter_mcu_list(self, filter_string):
            input_text = filter_string.upper()
            filtered = [mcu for mcu in self.supported_mcu_list if input_text in mcu]
            self._window['-MCU-'].update(values=filtered)

    def handle_events(self, event, values):
        retVal = True
        if event == sg.WIN_CLOSED:
            retVal = False
        if event == '-MCU-':
            self.current_mcu = values['-MCU-']
            self.mcu_filter_string = ""
        if event == '-MCU-KEYRELEASE-':
            self.mcu_filter_string = values['-MCU-']
            self.mcu_list_last_update_time = time.time()
        if event == '-CONNECT-':
            try:
                selected_mcu = self._window['-MCU-'].get()
                selected_interface = self._window['-INTERFACE-'].get()
                if self._rtt_handler.connect(selected_mcu, interface=selected_interface):
                    self._update_gui_status(True)
            except Exception as e:
                sg.popup_error(str(e))
        if event == '-DISCONNECT-':
            self._rtt_handler.disconnect()
            self._update_gui_status(False)
        if event == '-CLEAR-':
            self.log_handler['clear']()
            log_controller.clear_log_data()
        if event == '-FILTER-':
            self.filter_input_string = values['-FILTER-']
        if event == '-HIGHLIGHT-':
            # Update the log display when filter or highlight changes
            self.highlight_input_string = values['-HIGHLIGHT-']
        if event == '-PAUSE-':
            # Toggle pause state
            current_text = self._window['-PAUSE-'].GetText()
            new_text = 'Unpause' if current_text == 'Pause' else 'Pause'
            self._window['-PAUSE-'].update(new_text)
            # Trigger update to show accumulated messages if unpaused
            self.log_processing_input_queue.put({"pause_string": new_text})
        return retVal

    def run(self):
        # Start log processing thread
        processing_thread = threading.Thread(target=self._log_processing_thread, daemon=True)
        processing_thread.start()

        try:
            # GUI event loop
            while True:
                #time.sleep(0.1)

                # Check events
                event, values = self._window.read(timeout=100)
                if self.handle_events(event, values) == False:
                    break

                # Handle widget highlighting
                input_update = self.log_view.handle_widget_highlighting(self.filter_input_string, self.highlight_input_string, self.mcu_filter_string)
                if "mcu_string" in input_update:
                    # Check MCU filter
                    applied_mcu_filter_string = input_update["mcu_string"]
                    if applied_mcu_filter_string:
                        self._filter_mcu_list(applied_mcu_filter_string)

                # Handle log processing on input changes
                if input_update != {}:
                    self.log_processing_input_queue.put(input_update)

                # Update log
                current_time = time.time()
                if current_time - self.last_processed_time >= self.log_update_time_interval_s:
                    self._process_display_output_queue()
                    self.last_processed_time = current_time

        finally:
            self._rtt_handler.disconnect()
            self._window.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python RTT GUI')
    parser.add_argument('--demo-messages', action='store_true', help='Enable demo mode with sample log messages')
    args = parser.parse_args()

    viewer = RTTViewer(demo=args.demo_messages)
    viewer.run()
