#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular.
#
# Pin configuration for the Pico with LoRa-breakout.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------
import board

# --- standard pins RP2040   -------------------------------------------------

PIN_LED             = board.LED
PIN_VBUS_SENSE      = board.VBUS_SENSE
PIN_VOLTAGE_MONITOR = board.VOLTAGE_MONITOR

# --- pins needed for gateway-operation   ------------------------------------

PIN_SDA  = board.GP2
PIN_SCL  = board.GP3

PIN_LORA_SCK  = board.GP10
PIN_LORA_MISO = board.GP8
PIN_LORA_MOSI = board.GP11
PIN_LORA_CS   = board.GP9
PIN_LORA_RST  = board.GP7
