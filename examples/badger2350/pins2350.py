#-----------------------------------------------------------------------------
# Pin definitions for Pimoroni's Badger2350.
#
# These definitions are for the Badger2350 from Pimoroni
# https://shop.pimoroni.com/en-eu/products/badger-2350
# The board has an integrated display, RTC, a Stemma/Qt
# connector but no SD-card.
#
# Hardwired GPIOs include SDA/SCL and five buttons.
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
PIN_VOLTAGE_MONITOR = board.VBAT_SENSE

# --- pin-constants (don't change unless you know what you are doing)   ------

PIN_SDA0 = board.SDA
PIN_SCL0 = board.SCL   # connects to sensors and RTC (alternative bus)

# special pins:
# all buttons are active high
PIN_SWA = board.SW_A
PIN_SWA_ACTIVE_LOW = True
PIN_SWB = board.SW_B
PIN_SWB_ACTIVE_LOW = True
PIN_SWC = board.SW_C
PIN_SWC_ACTIVE_LOW = True

# no user-level LED
#PIN_SWD = board.SW_DOWN
