#!/usr/bin/env python3
"""
Final test to verify the interface-based approach works correctly
"""

import sys
import os

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

# Import the RTTViewer class
from python_rtt_gui import RTTViewer
from libs.jlink.rtt_handler import RTTHandler
from libs.jlink.demo_rtt_handler import DemoRTTHandler
from libs.jlink.rtt_handler_interface import RTTHandlerInterface

def test_interface():
    print("=== Testing Interface ===")
    
    # Test that both handlers implement the interface
    demo_handler = DemoRTTHandler()
    rtt_handler = RTTHandler()
    
    print(f"DemoRTTHandler implements RTTHandlerInterface: {isinstance(demo_handler, RTTHandlerInterface)}")
    print(f"RTTHandler implements RTTHandlerInterface: {isinstance(rtt_handler, RTTHandlerInterface)}")
    
    # Test that they both have required methods
    required_methods = ['connect', 'disconnect', 'get_supported_mcus', 'is_connected']
    
    for method in required_methods:
        print(f"DemoRTTHandler has {method}: {hasattr(demo_handler, method)}")
        print(f"RTTHandler has {method}: {hasattr(rtt_handler, method)}")
    
    return True

def test_demo_mode():
    print("\n=== Testing Demo Mode ===")
    viewer_demo = RTTViewer(demo=True)
    print(f"Demo mode current_mcu: {viewer_demo.current_mcu}")
    print(f"Demo mode supported_mcus: {viewer_demo.supported_mcu_list}")
    
    # Check if DEMO_MCU is in supported MCUs
    has_demo_mcu = 'DEMO_MCU' in viewer_demo.supported_mcu_list
    print(f"Has DEMO_MCU in supported MCUs: {has_demo_mcu}")
    
    # Check if default is DEMO_MCU
    is_demo_mcu_default = viewer_demo.current_mcu == 'DEMO_MCU'
    print(f"Default MCU is DEMO_MCU: {is_demo_mcu_default}")
    
    return has_demo_mcu and is_demo_mcu_default

def test_normal_mode():
    print("\n=== Testing Normal Mode ===")
    viewer_normal = RTTViewer(demo=False)
    print(f"Normal mode current_mcu: {viewer_normal.current_mcu}")
    print(f"Normal mode supported_mcus: {viewer_normal.supported_mcu_list}")
    
    # Check if default is STM32F427II
    is_stm32_default = viewer_normal.current_mcu == 'STM32F427II'
    print(f"Default MCU is STM32F427II: {is_stm32_default}")
    
    return is_stm32_default

if __name__ == "__main__":
    print("Testing final implementation with interface-based approach...")
    
    interface_ok = test_interface()
    demo_ok = test_demo_mode()
    normal_ok = test_normal_mode()
    
    print(f"\n=== Results ===")
    print(f"Interface test passed: {interface_ok}")
    print(f"Demo mode test passed: {demo_ok}")
    print(f"Normal mode test passed: {normal_ok}")
    
    if interface_ok and demo_ok and normal_ok:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)
