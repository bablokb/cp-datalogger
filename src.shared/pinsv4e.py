#-----------------------------------------------------------------------------
# Pin definitions for datalogger.
#
# Pinout for the DL-v4e.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import board

PCB_VERSION = 4       # version of special PCB of datalogger (use 0 otherwise)

# --- standard pins RP2040   -------------------------------------------------

PIN_LED             = board.LED
PIN_VBUS_SENSE      = board.VBUS_SENSE
PIN_VOLTAGE_MONITOR = board.VOLTAGE_MONITOR

# --- pin-constants (don't change unless you know what you are doing)   ------

PIN_SDA0  = board.GP0   # connect to sensors (alternative bus)
PIN_SCL0  = board.GP1   # connect to sensors (alternative bus)
PIN_SDA1  = board.GP2   # connect to sensors and RTC via I2C interface
PIN_SCL1  = board.GP3   # connect to sensors and RTC via I2C interface
PIN_DONE  = board.GP4   # INT pin (active low) of optional RTC

# SD-card interface (SPI)
PIN_SD_CS   = board.GP22
PIN_SD_SCK  = board.GP18
PIN_SD_MOSI = board.GP19
PIN_SD_MISO = board.GP16

# display interface
PIN_DISP_SCK  = board.GP18
PIN_DISP_MOSI = board.GP19
PIN_DISP_CS   = board.GP27
PIN_DISP_RST  = board.GP21
PIN_DISP_DC   = board.GP28
PIN_DISP_BUSY = board.GP26

# LoRA
PIN_LORA_CS   = board.GP9
PIN_LORA_RST  = board.GP13
PIN_LORA_DIO0 = board.GP15
PIN_LORA_SCK  = board.GP10
PIN_LORA_MOSI = board.GP11
PIN_LORA_MISO = board.GP12

# ETH interface (SPI)
PIN_ETH_RST  = board.GP20
PIN_ETH_CS   = board.GP17
PIN_ETH_SCK  = board.GP18
PIN_ETH_MOSI = board.GP19
PIN_ETH_MISO = board.GP16

# UART
PIN_RX = board.GP1
PIN_TX = board.GP0

# special pins:
# v4-boards: connect SWA-SWC to buttons
PIN_SWA = board.GP8
PIN_SWA_ACTIVE_LOW = True
PIN_SWB = board.GP6
PIN_SWB_ACTIVE_LOW = True
PIN_SWC = board.GP7
PIN_SWC_ACTIVE_LOW = True

# LED on PCB
PIN_SWD = board.GP5
