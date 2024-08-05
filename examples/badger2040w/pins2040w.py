#-----------------------------------------------------------------------------
# Pin definitions for Pimoroni's Badger2040W.
#
# These definitions are for the Badger2040W from Pimoroni
# https://shop.pimoroni.com/products/badger-2040-w
# The board has an integrated display, RTC, power-management, a Stemma/Qt
# connector but no SD-card.
#
# Hardwired GPIOs include SDA/SCL, DONE, and five buttons.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import board

PCB_VERSION = 0          # PCB-version of datalogger (i.e. no datalogger-PCB)

# --- standard pins RP2040   -------------------------------------------------

PIN_LED             = board.LED
PIN_VBUS_SENSE      = board.VBUS_SENSE
PIN_VOLTAGE_MONITOR = board.VOLTAGE_MONITOR

# --- pin-constants (don't change unless you know what you are doing)   ------

PIN_DONE = board.ENABLE_DIO
PIN_SDA0 = board.SDA
PIN_SCL0 = board.SCL   # connects to sensors and RTC (alternative bus)
PIN_SDA1 = board.GP2   # available, but unconnected
PIN_SCL1 = board.GP3   # available, but unconnected

# special pins:
# all buttons are active high
PIN_SWA = board.SW_A
PIN_SWA_ACTIVE_LOW = False
PIN_SWB = board.SW_B
PIN_SWB_ACTIVE_LOW = False
PIN_SWC = board.SW_C
PIN_SWC_ACTIVE_LOW = False

# no user-level LED
#PIN_SWD = board.SW_DOWN
