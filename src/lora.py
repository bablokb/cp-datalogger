#-----------------------------------------------------------------------------
# Setup of LoRa (adafruit_rfm9x.py)
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

    self._config = config
    # don't catch exceptions, main.py will handle that

    g_logger.print("LoRa: setting up SPI")
    spi1 = busio.SPI(pins.PIN_LORA_SCK,pins.PIN_LORA_MOSI,pins.PIN_LORA_MISO)
    pin_cs                = DigitalInOut(pins.PIN_LORA_CS)
    pin_reset             = DigitalInOut(pins.PIN_LORA_RST)

    if hasattr(pins,'PIN_LORA_EN'):
      g_logger.print("LoRa: enabling rfm9x")
      pin_enable = DigitalInOut(pins.PIN_LORA_EN)
      pin_enable.direction  = Direction.OUTPUT
      pin_enable.value = 1
      time.sleep(getattr(config,'LORA_ENABLE_TIME',0))

    g_logger.print("LoRa: initializing rfm9x")
    self.rfm9x = adafruit_rfm9x.RFM9x(
      spi1, pin_cs,pin_reset,config.LORA_FREQ,baudrate=100000)

    g_logger.print("LoRa: configuring rfm9x")
    self.rfm9x.enable_crc = True
    self.rfm9x.tx_power = config.LORA_TX_POWER
    self.rfm9x.node = config.LORA_NODE_ADDR                      # this
    self.rfm9x.destination = getattr(config,"LORA_BASE_ADDR",0)  # gateway
    self.rfm9x.ack_wait = getattr(config,'LORA_ACK_WAIT',0.25)
    self.rfm9x.ACK_DELAY = getattr(config,"LORA_ACK_DELAY",0.1)
    self.rfm9x.ack_retries = getattr(config,"LORA_ACK_RETRIES",3)
    self.rfm9x.sleep()

  # --- transmit command   ---------------------------------------------------

  def transmit(self,string,ack=True,keep_listening=False):
    """ send data """
    if getattr(self._config,'TEST_MODE',False) or getattr(self._config,'DEV_MODE',False):
      g_logger.print("LoRa: sending data...")
    if ack:
      return self.rfm9x.send_with_ack(bytes(string, "UTF-8"))
    else:
      return self.rfm9x.send(bytes(string, "UTF-8"),keep_listening=keep_listening)

  # --- receive command   ----------------------------------------------------

  def receive(self,with_ack=True,timeout=0.5):
    """ receive and decode data """
    if getattr(self._config,'TEST_MODE',False) or getattr(self._config,'DEV_MODE',False):
      g_logger.print("LoRa: receiving data...")
    packet = self.rfm9x.receive(with_ack=with_ack,timeout=timeout)
    if packet is None:
      return (None,None,None)
    else:
      if getattr(self._config,'TEST_MODE',False) or getattr(self._config,'DEV_MODE',False):
        g_logger.print(f"LoRa: packet: {packet.decode()}")
      return (packet.decode(),self.rfm9x.last_snr,self.rfm9x.last_rssi)

  # --- set destination   ----------------------------------------------------

  def set_destination(self,dest):
    """ set destination for transmit """
    self.rfm9x.destination = dest
