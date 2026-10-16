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
BAT_SAMPLES = 10         # from Pimoronis implementation

# --- standard pins RP2350   -------------------------------------------------

PIN_LED             = board.LED
PIN_VBUS_SENSE      = board.VBUS_SENSE

# --- special logic for battery level   --------------------------------------

def bat_level():
  """ return battery level """
  from analogio import AnalogIn

  sum_vbat = 0
  sum_vref = 0
  adc_vbat = AnalogIn(board.VBAT_SENSE)
  adc_vref = AnalogIn(board.SENSE_1V1)

  for _ in range(BAT_SAMPLES):
    sum_vbat += adc_vbat.value
    sum_vref += adc_vref.value
  adc_vbat.deinit()
  adc_vref.deinit()
  return 2.2*sum_vbat/sum_vref

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
