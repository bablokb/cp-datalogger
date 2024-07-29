#-----------------------------------------------------------------------------
# Pin definitions for datalogger.
#
# These definitions are specific to the datalogger hardware. If you run the
# software on a different hardware-basis, adapt this to your needs.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import board

PCB_VERSION = 1          # PCB-version of datalogger

# --- standard pins RP2040   -------------------------------------------------

PIN_LED             = board.LED
PIN_VBUS_SENSE      = board.VBUS_SENSE
PIN_VOLTAGE_MONITOR = board.VOLTAGE_MONITOR

# --- pin-constants (don't change unless you know what you are doing)   ------

PIN_DONE = board.GP4   # connect to 74HC74 CLK
PIN_SDA0  = board.GP0   # connect to sensors (alternative bus)
PIN_SCL0  = board.GP1   # connect to sensors (alternative bus)
PIN_SDA1  = board.GP2   # connect to sensors and RTC via I2C interface
PIN_SCL1  = board.GP3   # connect to sensors and RTC via I2C interface

# SD-card interface (SPI)
PIN_SD_CS   = board.GP22
PIN_SD_SCK  = board.GP18
PIN_SD_MOSI = board.GP19
PIN_SD_MISO = board.GP16

# display interface (SPI, Inky-Pack)
PIN_INKY_CS   = board.GP17
PIN_INKY_RST  = board.GP21
PIN_INKY_DC   = board.GP20
PIN_INKY_BUSY = board.GP26

PIN_LORA_CS   = board.GP9
PIN_LORA_RST  = board.GP7
PIN_LORA_EN   = board.GP15
PIN_LORA_SCK  = board.GP10
PIN_LORA_MOSI = board.GP11
PIN_LORA_MISO = board.GP8

# PDM-mic
PIN_PDM_CLK = board.GP5
PIN_PDM_DAT = board.GP28

# UART
PIN_RX = board.GP1
PIN_TX = board.GP0

# 1-wire
PIN_ONE_WIRE = board.GP27

# special pins:
# v1-boards: connects SWA-SWC to the display
PIN_SWA = board.GP12
PIN_SWA_ACTIVE_LOW = True
PIN_SWB = board.GP13
PIN_SWB_ACTIVE_LOW = True
PIN_SWC = board.GP14
PIN_SWC_ACTIVE_LOW = True

# connected with LRCL, but unused
#PIN_SWD = board.GP6
