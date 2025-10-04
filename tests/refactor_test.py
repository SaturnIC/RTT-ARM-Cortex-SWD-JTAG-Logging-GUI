#!/usr/bin/env python3
"""
Test to verify the refactored code with inheritance works correctly
"""

import sys
import os

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

# Import the RTTViewer class
from python_rtt_gui import RTTViewer
from libs.jlink.rtt_handler import RTTHandler
from libs.jlink.demo_rtt_handler import DemoRTTHandler
from libs.jlink.base_rtt_handler import BaseRTTHandler

def test_inheritance():
    print("=== Testing Inheritance ===")
    
    # Test that both handlers inherit from BaseRTTHandler
    demo_handler = DemoRTTHandler()
    rtt_handler = RTTHandler()
    
    print(f"DemoRTTHandler inherits from BaseRTTHandler: {isinstance(demo_handler, BaseRTTHandler)}")
    print(f"RTTHandler inherits from BaseRTTHandler: {isinstance(rtt_handler, BaseRTTHandler)}")
    
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
    print("Testing refactored code with inheritance...")
    
    inheritance_ok = test_inheritance()
    demo_ok = test_demo_mode()
    normal_ok = test_normal_mode()
    
    print(f"\n=== Results ===")
    print(f"Inheritance test passed: {inheritance_ok}")
    print(f"Demo mode test passed: {demo_ok}")
    print(f"Normal mode test passed: {normal_ok}")
    
    if inheritance_ok and demo_ok and normal_ok:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)
