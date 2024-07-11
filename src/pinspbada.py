#-----------------------------------------------------------------------------
# Pin definitions for datalogger.
#
# These definitions are for the Adafruit PiCowbell Adalogger
# https://www.adafruit.com/product/5703. This board provides a PCF8523 RTC,
# a SD-card slot and a Stemma/Qt connector.
#
# The only hardwired GPIOs are SDA0, SCL0 and PIN_SD_xxx.
# Powermanagement is available by adding a TPL5110/TPL5111. Note that the
# DONE-pin does not seem to work with ADC-pins.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import board

PCB_VERSION = 0          # PCB-version of datalogger (i.e. no datalogger-PCB)

# --- pin-constants (don't change unless you know what you are doing)   ------

PIN_DONE = board.GP6   # connect to DONE-pin of TPL5110/TPL5111
PIN_SDA0 = board.GP4   # connects to sensors and RTC (alternative bus)
PIN_SCL0 = board.GP5   # connects to sensors and RTC (alternative bus)
PIN_SDA1 = board.GP2   # connect to sensors
PIN_SCL1 = board.GP3   # connect to sensors

# SD-card interface (SPI)
PIN_SD_CS   = board.GP17
PIN_SD_SCK  = board.GP18
PIN_SD_MOSI = board.GP19
PIN_SD_MISO = board.GP16

# display interface (SPI, e-inks, not Inky-Pack compatible)
PIN_INKY_CS   = board.GP22    # use GP17 for Inky-Pack if the SD-card is unused
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
PIN_SWB = board.GP13
PIN_SWC = board.GP14
#PIN_SWD = board.GP6
