"""
Main test suite for RTT GUI functionality
Tests the core functionality including demo mode, normal mode, and MCU selection
"""

import sys
import os
import pytest

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rtt_python_gui import RTTViewer
from libs.jlink.rtt_handler import RTTHandler
from libs.jlink.demo_rtt_handler import DemoRTTHandler
from libs.jlink.rtt_handler_interface import RTTHandlerInterface


class TestRTTViewer:
    """Test RTTViewer class functionality"""
    
    def test_interface_implementation(self):
        """Test that both handlers implement the interface correctly"""
        demo_handler = DemoRTTHandler(None)
        rtt_handler = RTTHandler(None)
        
        # Test that both handlers implement the interface
        assert isinstance(demo_handler, RTTHandlerInterface)
        assert isinstance(rtt_handler, RTTHandlerInterface)
        
        # Test that they both have required methods
        required_methods = ['connect', 'disconnect', 'get_supported_mcus', 'is_connected']
        
        for method in required_methods:
            assert hasattr(demo_handler, method)
            assert hasattr(rtt_handler, method)
    
    def test_demo_mode_initialization(self):
        """Test that demo mode initializes correctly"""
        viewer_demo = RTTViewer(demo=True)
        
        # Check that DEMO_MCU is in supported MCUs
        assert 'DEMO_MCU' in viewer_demo.supported_mcu_list
        
        # Check that demo mode has the expected MCU list
        assert len(viewer_demo.supported_mcu_list) > 0
    
    def test_normal_mode_initialization(self):
        """Test that normal mode initializes correctly"""
        viewer_normal = RTTViewer(demo=False)
        
        # Check that normal mode has the expected MCU list
        assert len(viewer_normal.supported_mcu_list) > 0
    
    def test_mcu_selection(self):
        """Test MCU selection functionality"""
        viewer = RTTViewer(demo=True)
        
        # Test that we can access the supported MCUs list
        assert len(viewer.supported_mcu_list) > 0


class TestRTTViewerIntegration:
    """Integration tests for RTTViewer"""
    
    def test_demo_mode_functionality(self):
        """Test demo mode specific functionality"""
        viewer_demo = RTTViewer(demo=True)
        
        # Verify DEMO_MCU is in supported MCUs
        assert 'DEMO_MCU' in viewer_demo.supported_mcu_list
    
    def test_normal_mode_functionality(self):
        """Test normal mode specific functionality"""
        viewer_normal = RTTViewer(demo=False)
        
        # Verify STM32F427II is in supported MCUs
        assert 'STM32F427II' in viewer_normal.supported_mcu_list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
