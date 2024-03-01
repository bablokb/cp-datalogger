#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular.
#
# Pin configuration for generic Feather-MCUs (e.g. SWAN R5)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------
import board

PIN_SDA  = board.SDA
PIN_SCL  = board.SCL

PIN_LORA_SCK  = board.SCK
PIN_LORA_MISO = board.MISO
PIN_LORA_MOSI = board.MOSI
PIN_LORA_CS   = board.A5
PIN_LORA_RST  = board.A4
