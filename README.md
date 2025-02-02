# Python RTT GUI
![RTT GUI](./docs/python_rtt_gui.png)

A Python-based GUI application for Real-Time Transfer (RTT) communication with MCUs using J-Link.
This project provides a simple and intuitive interface for connecting to and monitoring target MCUs.


## Features

- Connects to MCUs using J-Link debuggers
- Real-time log display for RTT data
- Support for filtering and selecting MCUs
- Simple and clean GUI interface
- Status monitoring and connection management

## Prerequisites
- Python 3.8+ (https://www.python.org/)
- J-Link software suite installed (https://www.segger.com/downloads/jlink)
- Required Python packages:
  - PySimpleGUI
  - pylink (Segger's J-Link Python wrapper)

### Use RTTViewer in Embedded Target
- RTT source code is available in the J-Link Software and Documentation Pack,
  under the following code `JLink/Samples/RTT`
- Include this code into your embedded project and use the SEGGER_RTT_printf function to print log
  messages to the JLink host:
  ```C
  # include SEGGER_RTT.h

  SEGGER_RTT_SetTerminal(0);
  SEGGER_RTT_printf(0, "%s\n", "Hello from embedded MCU");
  ```

## GUI Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-rtt-gui.git
   cd python-rtt-gui
   ```

2. Install the required packages:
   ```bash
   pip install PySimpleGUI pylink

   # or
   pip install -r requirements.txt
   ```

3. Ensure J-Link software is installed and accessible on your system.

## Usage

1. Run the application:
   ```bash
   python python_rtt_gui.py
   ```

2. Select your target MCU from the dropdown list.

3. Click "Connect" to establish a connection.

4. Use the "Disconnect" button to terminate the connection.

5. Use the "Clear" button to reset the log display.

6. Filter MCUs by typing in the MCU selection field.

## License

This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for more details.

## Contact

For questions, issues, or contributions, please contact the maintainer

---

**Note:** Make sure J-Link is properly installed and accessible on your system. The application requires J-Link's Python wrapper (`pylink`) to communicate with the debugger.