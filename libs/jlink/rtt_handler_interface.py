from abc import ABC, abstractmethod
import queue

class RTTHandlerInterface(ABC):
    """
    Abstract base class for RTT handlers.
    Defines the interface that all RTT handlers must implement.
    """
    
    def __init__(self, log_processing_input_queue):
        self._log_queue = log_processing_input_queue
        self._supported_mcu_list = []
    
    @abstractmethod
    def connect(self, mcu_name, interface='SWD', block_address=None, print_function=None):
        """
        Connect to the specified MCU and start RTT.
        
        Args:
            mcu_name (str): Name of the MCU to connect to.
            interface (str): Interface to use ('SWD' or 'JTAG').
            block_address (int, optional): Address of the RTT control block.
            print_function: Function to print messages.
            
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the MCU and stop RTT.
        """
        pass
    
    @abstractmethod
    def get_supported_mcus(self):
        """
        Get the list of supported MCUs.
        
        Returns:
            List of MCU strings.
        """
        pass
    
    @property
    @abstractmethod
    def is_connected(self):
        """
        Check if currently connected to an MCU.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        pass
    
    @property
    def log_queue(self):
        """
        Get the queue containing RTT log data.
        
        Returns:
            queue.Queue: Queue with RTT data.
        """
        return self._log_queue
    
    @property
    def supported_mcu_list(self):
        """
        Get the list of supported MCUs.
        
        Returns:
            List of MCU strings.
        """
        return self._supported_mcu_list
