#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from python_rtt_gui import RTTViewer

# Test that demo mode sets MCU to DEMO_MCU
print("Testing demo mode initialization...")
viewer_demo = RTTViewer(demo=True)
print(f"Demo mode current_mcu: {viewer_demo.current_mcu}")
print(f"Demo mode supported_mcus: {viewer_demo.supported_mcu_list}")

# Test that normal mode sets MCU to STM32F427II
print("\nTesting normal mode initialization...")
viewer_normal = RTTViewer(demo=False)
print(f"Normal mode current_mcu: {viewer_normal.current_mcu}")
print(f"Normal mode supported_mcus: {viewer_normal.supported_mcu_list}")

# Verify DEMO_MCU is in demo mode supported MCUs
if 'DEMO_MCU' in viewer_demo.supported_mcu_list:
    print("\n✓ DEMO_MCU found in demo mode supported MCUs")
else:
    print("\n✗ DEMO_MCU NOT found in demo mode supported MCUs")

# Verify default MCU selection
if viewer_demo.current_mcu == 'DEMO_MCU':
    print("✓ Demo mode correctly sets default MCU to DEMO_MCU")
else:
    print("✗ Demo mode does not set default MCU to DEMO_MCU")

if viewer_normal.current_mcu == 'STM32F427II':
    print("✓ Normal mode correctly sets default MCU to STM32F427II")
else:
    print("✗ Normal mode does not set default MCU to STM32F427II")

print("\nTest completed.")
