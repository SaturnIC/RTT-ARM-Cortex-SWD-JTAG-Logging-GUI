import pylink
import threading
import queue
import time

class RTTHandler:
    def __init__(self):
        self._jlink = pylink.JLink()
        self._supported_mcu_list = [self._jlink.supported_device(i).name.lower() for i in range(self._jlink.num_supported_devices())]
        self._log_queue = queue.Queue()
        self._connected = False
        self._rtt_thread = None

    def connect(self, mcu_name, block_address=None, print_function = None):
        """
        Connect to the specified MCU and start RTT.

        Args:
            mcu_name (str): Name of the MCU to connect to.
            block_address (int, optional): Address of the RTT control block.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        try:
            self._jlink.open()
            print_function("connecting to %s...\n" % mcu_name)
            self._jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            self._jlink.connect(mcu_name)
            print_function("connected, starting RTT...\n")
            self._jlink.rtt_start(block_address)
            self._connected = True

            # Start RTT read thread
            self._rtt_thread = threading.Thread(
                target=self._read_rtt,
                daemon=True
            )
            self._rtt_thread.start()

            return True
        except pylink.JLinkException as e:
            self.disconnect()
            raise Exception(f'Connection failed: {str(e)}')

    def disconnect(self):
        """
        Disconnect from the MCU and stop RTT.
        """
        if self._connected:
            self._jlink.close()
            self._connected = False

    def _read_rtt(self):
        """
        Continuously read RTT data and put it into the log queue.
        """
        while self._connected:
            try:
                data = self._jlink.rtt_read(0, 1024)
                if data:
                    byte_string = bytes(data)
                    latin_string = byte_string[2:].decode('latin-1') # first two bytes used in header?
                    self._log_queue.put(latin_string)
                time.sleep(0.1)
            except pylink.JLinkException:
                break

    def get_supported_mcus(self):
        """
        Get the list of supported MCUs.

        Returns:
            List of MCU strings.
        """
        return self._supported_mcu_list

    @property
    def is_connected(self):
        """
        Check if currently connected to an MCU.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._connected

    @property
    def log_queue(self):
        """
        Get the queue containing RTT log data.

        Returns:
            queue.Queue: Queue with RTT data.
        """
        return self._log_queue