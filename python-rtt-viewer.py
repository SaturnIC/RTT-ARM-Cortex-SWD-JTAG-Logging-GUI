import PySimpleGUI as sg
import pylink
import threading
import queue
import time

# Initialize PyLink
jlink = pylink.JLink()

# List of common MCUs (you can expand this list)
mcu_list = [
    "STM32F427II",
    "STM32F429II",
    "STM32F407VG",
    "STM32F417VE",
    "STM32F427VG",
    "STM32F437VG",
    "STM32F439ZG",
    "STM32F446RE",
    "STM32F446VE",
    "STM32F446ZE"
]

# GUI setup
sg.theme('Dark Gray 13')
layout = [
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

window = sg.Window('RTT Viewer', layout, finalize=True)

# Queue for log updates
log_queue = queue.Queue()

# Thread to read RTT data
def read_rtt(jlink):
    while True:
        try:
            data = jlink.rtt_read(0, 1024)
            if data:
                byte_string = bytes(data)
                latin_string = byte_string.decode('latin-1')
                log_queue.put(latin_string)
            time.sleep(0.1)
        except pylink.JLinkException:
            break

# Connect function
def connect(block_address=None):
    try:
        # Get selected MCU from dropdown
        selected_mcu = window['-MCU-'].get()

        # Connect to MCU
        jlink = pylink.JLink()
        print("connecting to JLink...")
        jlink.open()
        print("connecting to %s..." % selected_mcu)
        jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        jlink.connect(selected_mcu)
        print("connected, starting RTT...")
        jlink.rtt_start(block_address)

        window['-STATUS-'].update('Status: Connected')
        window['-CONNECT-'].update(disabled=True)
        window['-DISCONNECT-'].update(disabled=False)

        # Start RTT thread
        rtt_thread = threading.Thread(target=read_rtt, daemon=True, args=[jlink])
        rtt_thread.start()
    except pylink.JLinkException as e:
        sg.popup_error(f'Connection failed: {str(e)}')

# Disconnect function
def disconnect():
    jlink.close()
    window['-STATUS-'].update('Status: Disconnected')
    window['-CONNECT-'].update(disabled=False)
    window['-DISCONNECT-'].update(disabled=True)

# Main event loop
while True:
    event, values = window.read(timeout=100)
    
    if event == sg.WIN_CLOSED:
        break
    
    if event == '-CONNECT-':
        connect()
    
    if event == '-DISCONNECT-':
        disconnect()
    
    if event == '-CLEAR-':
        window['-LOG-'].update('')
    
    # Update log
    if not log_queue.empty():
        try:
            data = log_queue.get_nowait()
            window['-LOG-'].update(data, append=True)
        except queue.Empty:
            pass

window.close()