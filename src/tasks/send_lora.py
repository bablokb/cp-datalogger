#-----------------------------------------------------------------------------
# Task: send data using LoRa (adafruit_rfm9x.py)
#
# Authors: Syed Omer Ali, Björn Haßler
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

from singleton import singleton

from digitalio import DigitalInOut, Direction, Pull
import busio
import time
import adafruit_rfm9x
import pins

# --- helper class for LoRa   ------------------------------------------------

@singleton
class LORA:
  def __init__(self,config):
    """ constructor """

    # don't catch exceptions, main.py will handle that

    g_logger.print("LoRa: setting up SPI1")
    spi1 = busio.SPI(pins.PIN_LORA_SCK,pins.PIN_LORA_MOSI,pins.PIN_LORA_MISO)
    pin_cs                = DigitalInOut(pins.PIN_LORA_CS)
    pin_reset             = DigitalInOut(pins.PIN_LORA_RST)
    pin_enable            = DigitalInOut(pins.PIN_LORA_EN)
    pin_enable.direction  = Direction.OUTPUT

    g_logger.print("LoRa: enabling rfm9x")
    pin_enable.value = 1
    time.sleep(config.LORA_ENABLE_TIME)
    g_logger.print("LoRa: nitializing rfm9x")
    self.rfm9x = adafruit_rfm9x.RFM9x(
      spi1, pin_cs,pin_reset,config.LORA_FREQ,baudrate=100000)
      
    g_logger.print("LoRa: configuring rfm9x")
    self.rfm9x.enable_crc = True
    #self.rfm9x.tx_power = 23
    self.rfm9x.ack_delay = 0.1
    self.rfm9x.node = config.LORA_NODE_ADDR                 # node or this device
    self.rfm9x.destination = config.LORA_BASE_ADDR  # base station or destination
    self.rfm9x.ack_wait = config.LORA_ACK_WAIT
    self.rfm9x.ack_retries = config.LORA_ACK_RETRIES
    self.rfm9x.sleep()

  # --- transmit command   ----------------------------------------------

  def transmit(self, header, string):
    """ send data """
    g_logger.print("LoRa: sending data...")
    send_ok = self.rfm9x.send_with_ack(bytes(string, "UTF-8"))
    if send_ok:
      g_logger.print("LoRa: ... successful")
    else:
      g_logger.print("LoRa: ... failed")

def run(config,app):
  """ send data using LoRa """
  lora = LORA(config)
  lora.transmit(app.csv_header,app.record)
