#-----------------------------------------------------------------------------
# LoRa gateway with Blues cellular.
#
# Pin configuration for the Challenger-RP2040-LORA
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------
import board

PIN_SDA  = board.SDA
PIN_SCL  = board.SCL

PIN_LORA_SCK  = board.RFM95W_SCK
PIN_LORA_MISO = board.RFM95W_SDI
PIN_LORA_MOSI = board.RFM95W_SDO
PIN_LORA_CS   = board.RFM95W_CS
PIN_LORA_RST  = board.RFM95W_RST
