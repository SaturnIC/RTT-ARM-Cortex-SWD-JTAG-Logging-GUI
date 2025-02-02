import PySimpleGUI as sg
import time
import queue
import time
from libs.jlink.rtt_handler import RTTHandler


# constants
FILTER_APPLICATION_WAIT_TIME_s = 1


class RTTGui:
    def __init__(self):
        # Initialize RTT Handler
        self._rtt_handler = RTTHandler()
        self.supported_mcu_list = self._rtt_handler.get_supported_mcus()

        # GUI setup
        sg.theme('Dark Gray 13')
        self._layout = [
            [sg.Text('Python RTT GUI', size=(30, 1), justification='center')],
            [sg.Column([
                [sg.Text('MCU Chip Name:'),
                 sg.Combo(self.supported_mcu_list, default_value='STM32F427II',
                          key='-MCU-', size=(20, 1), enable_events=True)]
            ])],
            [sg.Output(size=(80, 20), key='-LOG-', font=('Consolas', 10))],
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

        # Bind the <KeyRelease> event to the Combo widget.
        # This will write a new event '-COMBO-KEYRELEASE-' to the window's event queue whenever a key is released.
        self._window['-MCU-'].Widget.bind("<KeyRelease>", lambda event: self._window.write_event_value('-MCU-KEYRELEASE-', event))

    def _update_gui_status(self, connected):
        """
        Update the GUI elements based on connection status.
        Args:
            connected (bool): True if connected, False otherwise.
        """
        self._window['-STATUS-'].update(
            'Status: Connected' if connected else 'Status: Disconnected'
        )
        self._window['-CONNECT-'].update(disabled=connected)
        self._window['-DISCONNECT-'].update(disabled=not connected)

    def _append_to_log(self, message):
        self._window['-LOG-'].update(message, append=True)

    def _process_log_queue(self):
        """
        Process the log queue and update the output window.
        """
        while not self._rtt_handler.log_queue.empty():
            try:
                data = self._rtt_handler.log_queue.get_nowait()
                self._append_to_log(data)
            except queue.Empty:
                pass

    def _filter_mcu_list(self, filter_string):
        if (time.time() - self.mcu_list_last_update_time) > FILTER_APPLICATION_WAIT_TIME_s:
            input_text = filter_string.lower()
            filtered = [mcu for mcu in self.supported_mcu_list
                        if input_text in mcu.lower()]
            self._window['-MCU-'].update(values=filtered)

    def run(self):
        """
        Start the GUI event loop.
        """
        try:
            while True:
                time.sleep(0.001)

                # Check MCU filter
                if self.mcu_filter_string != "":
                    if (time.time() - self.mcu_list_last_update_time) > FILTER_APPLICATION_WAIT_TIME_s:
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
                        if self._rtt_handler.connect(selected_mcu, print_function = self._append_to_log):
                            self._update_gui_status(True)
                    except Exception as e:
                        sg.popup_error(str(e))
                if event == '-DISCONNECT-':
                    self._rtt_handler.disconnect()
                    self._update_gui_status(False)
                if event == '-CLEAR-':
                    self._window['-LOG-'].update('')
                # Update log
                self._process_log_queue()
        finally:
            self._rtt_handler.disconnect()
            self._window.close()

if __name__ == "__main__":
    viewer = RTTGui()
    viewer.run()