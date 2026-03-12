#-----------------------------------------------------------------------------
# Pin definitions for datalogger.
#
# This is a QT-Py ESP32S3 with XIAO-Base.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import board

PCB_VERSION = 0       # version of special PCB of datalogger (use 0 otherwise)

# --- standard pins RP2040   -------------------------------------------------

PIN_LED             = board.LED
#PIN_VOLTAGE_MONITOR = board.VOLTAGE_MONITOR

# --- pin-constants (don't change unless you know what you are doing)   ------

PIN_SDA1  = board.D4   # connect to sensors and RTC via I2C interface
PIN_SCL1  = board.D5   # connect to sensors and RTC via I2C interface

# SD-card interface (SPI)
PIN_SD_CS   = board.D2
PIN_SD_SCK  = board.SCK
PIN_SD_MOSI = board.MOSI
PIN_SD_MISO = board.MISO

# UART
PIN_RX = board.D7
PIN_TX = board.D6

# special pins:
# v3-boards: connect SWA-SWC to buttons
PIN_SWA = board.D1
PIN_SWA_ACTIVE_LOW = True
