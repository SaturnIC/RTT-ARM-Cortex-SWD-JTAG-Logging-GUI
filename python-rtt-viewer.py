import PySimpleGUI as sg
import time
from libs.jlink.rtt_handler import RTTHandler
from libs.jlink.supported_mcus import mcu_list

class RTTViewer:
    def __init__(self):

        # Initialize RTT Handler
        self._rtt_handler = RTTHandler()

        # GUI setup
        sg.theme('Dark Gray 13')
        self._layout = [
            [sg.Text('Segger RTT Viewer', size=(30, 1), justification='center')],
            [sg.Column([
                [sg.Text('MCU Chip Name:'),
                 sg.Combo(mcu_list, default_value='STM32F427II', key='-MCU-', size=(20, 1))]
            ])],
            [sg.Output(size=(80, 20), key='-LOG-', font=('Consolas', 10))],
            [sg.Column([
                [sg.Button('Connect', key='-CONNECT-'),
                 sg.Button('Disconnect', key='-DISCONNECT-', disabled=True),
                 sg.Button('Clear', key='-CLEAR-'),
                 sg.Text('Status: Disconnected', key='-STATUS-', size=(20, 1))]
            ])]
        ]
        self._window = sg.Window('RTT Viewer', self._layout, finalize=True)

        # Initialize GUI state
        self._update_gui_status(False)

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

    def _process_log_queue(self):
        """
        Process the log queue and update the output window.
        """
        while not self._rtt_handler.log_queue.empty():
            try:
                data = self._rtt_handler.log_queue.get_nowait()
                self._window['-LOG-'].update(data, append=True)
            except queue.Empty:
                pass

    def run(self):
        """
        Start the GUI event loop.
        """
        try:
            while True:
                event, values = self._window.read(timeout=100)

                if event == sg.WIN_CLOSED:
                    break

                if event == '-CONNECT-':
                    try:
                        selected_mcu = values['-MCU-']
                        if self._rtt_handler.connect(selected_mcu):
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
    viewer = RTTViewer()
    viewer.run()