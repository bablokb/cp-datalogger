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

# --- standard pins RP2040   -------------------------------------------------

PIN_LED             = board.LED
#PIN_VBUS_SENSE      = board.VBUS_SENSE         # not defined
#PIN_VOLTAGE_MONITOR = board.VOLTAGE_MONITOR    # not defined

# --- pins needed for gateway-operation   ------------------------------------

PIN_SDA1  = board.SDA
PIN_SCL1  = board.SCL

PIN_LORA_SCK  = board.RFM95W_SCK
PIN_LORA_MISO = board.RFM95W_SDI
PIN_LORA_MOSI = board.RFM95W_SDO
PIN_LORA_CS   = board.RFM95W_CS
PIN_LORA_RST  = board.RFM95W_RST

PIN_RX = board.RX
PIN_TX = board.TX

# SD-card interface (SPI0)
PIN_SD_CS   = board.A5      # GP21, F_A5
PIN_SD_SCK  = board.SCK     # GP22, F_SCK
PIN_SD_MOSI = board.MOSI    # GP23, F_MOSI
PIN_SD_MISO = board.MISO    # GP20, F_MISO

# alternative (SPI0)
#PIN_SD_CS   = board.GP5    # F_D10
#PIN_SD_SCK  = board.GP2    # F_D5
#PIN_SD_MOSI = board.GP3    # F_D6
#PIN_SD_MISO = board.GP4    # F_9
