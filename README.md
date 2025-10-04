# ARM Cortex SWD RTT GUI
![RTT GUI Screenshot](./docs/python_rtt_gui.png)

**Open-source Python GUI for ARM Cortex SWD Debug Channel**

This project provides a Python-based GUI interface for SEGGER's Real-Time Transfer (RTT) debug protocol, enabling direct communication with ARM Cortex-based microcontrollers via J-Link debug probes. It replaces traditional debug channels (like UART) with the efficient SWD/SWO interface without requiring intermediary applications.

As one of the few projects that directly interfaces with J-Link using Segger's Python wrapper (`pylink`) to receive RTT messages, it displays real-time logs from embedded targets with filtering and highlighting capabilities. Since messages are processed in Python, this foundation can be extended to support advanced features like data plotting and analysis - capabilities not available in SEGGER's standard RTT applications.


This project serves as a wrapper for SEGGER Real-Time Transfer (RTT) debug channel,
demonstrating how to replace clunky classical MCU debug channels like UART with lean and mean SWD, SWO
for ARM MCUs
without the need for any intermediary applications.

This project can be used as a foundation to create a custom debug communication tool for ARM MCU development.

The documentation and examples in pylink, SEGGER's Python wrapper, are severely lacking when it comes to using the RTT channel, so this project may also serve as a guide to help leverage pylink for RTT.

## Key Features
- Direct J-Link connection using native drivers (no RTTViewer required)
- Real-time display of debug communication
- Log filtering and message highlighting
- Broad MCU support through intuitive selection interface
- Connection status monitoring and management
- Extensible architecture for custom processing (plotting, analysis, etc.)

## Prerequisites

### Host Software
- Python 3.8+ (https://www.python.org/)
- SEGGER J-Link Software ([Download](https://www.segger.com/downloads/jlink))
- Required Python packages (Defined in requirements.txt file):
  - FreeSimpleGUI
  - pylink (Segger's J-Link Python wrapper)

### Embedded Target Setup
Include RTT in your firmware using the source code from `JLink/Samples/RTT` (included in J-Link installation):
```c
#include "SEGGER_RTT.h"

void main() {
    SEGGER_RTT_Init();
    SEGGER_RTT_SetTerminal(0);
    SEGGER_RTT_printf(0, "System started\n");
}
```

## GUI Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SaturnIC/JLink-RTT-Python-GUI.git
   cd python-rtt-gui
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt

   # or explicitly
   pip install FreeSimpleGUI==5.0.0 pylink
   ```
3. Ensure that the J-Link drivers are installed and accessible on your system.

## Usage

### Start Logging
1. Launch the application:
   ```bash
   python python_rtt_gui.py
   ```

2. Select your target MCU from the dropdown list.
   Filter MCU list by typing a matching substring in the MCU dropdown widget.

3. Click "Connect" to establish a connection.

### Highlight Logs
Enter text in highlight box to highlight matching messages

### Filter Logs
Filter log messages by entering a filter substring in the filter box

### Disconnect From MCU
Use the "Disconnect" button to terminate the connection.

### Clear the Log View
Use the "Clear" button to reset the log display.


## License

This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for more details.

## Contact

For questions, issues, or contributions, please contact the maintainer

---

**Note:** Requires properly installed J-Link drivers. The application communicates directly with debug hardware using SEGGER's `pylink` Python wrapper.