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
    self._trace = getattr(self._config,'LORA_TRACE',False)

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
    self.rfm9x.tx_power = getattr(config,"LORA_TX_POWER",13)
    self.rfm9x.node = config.LORA_NODE_ADDR                      # this
    self.rfm9x.destination = getattr(config,"LORA_BASE_ADDR",0)  # gateway
    self.rfm9x.ack_wait = getattr(config,'LORA_ACK_WAIT',0.25)
    self.rfm9x.ACK_DELAY = getattr(config,"LORA_ACK_DELAY",0.1)
    self.rfm9x.ack_retries = getattr(config,"LORA_ACK_RETRIES",3)
    self.rfm9x.sleep()

  # --- trace LoRa-events   --------------------------------------------------

  def trace(self,msg):
    """ trace LoRa events """
    if self._trace:
      g_logger.print(msg)

  # --- transmit command   ---------------------------------------------------

  def transmit(self,string,ack=True,keep_listening=False):
    """ send data """
    self.trace(f"LoRa: sending data: {string}")
    if ack:
      return self.rfm9x.send_with_ack(bytes(string, "UTF-8"))
    else:
      return self.rfm9x.send(bytes(string, "UTF-8"),keep_listening=keep_listening)

  # --- receive command   ----------------------------------------------------

  def receive(self,with_ack=True,timeout=0.5):
    """ receive and decode data """
    self.trace("LoRa: receiving data...")
    packet = self.rfm9x.receive(with_ack=with_ack,timeout=timeout)
    if packet is None:
      self.trace(f"LoRa: no packet within {timeout}s")
      return (None,None,None)
    else:
      self.trace(f"LoRa: packet: {packet.decode()}")
      return (packet.decode(),self.rfm9x.last_snr,self.rfm9x.last_rssi)

  # --- set destination   ----------------------------------------------------

  def set_destination(self,dest):
    """ set destination for transmit """
    self.rfm9x.destination = dest

  # --- broadcast a package and wait for response   --------------------------

  def broadcast(self,nr,timeout=10):
    """ send a broadcast package """

    ts = time.localtime()
    ts_str = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}T{ts.tm_hour:02d}:{ts.tm_min:02d}:{ts.tm_sec:02d}"

    # send packet ("B",TS,ID,nr,node)
    g_logger.print(f"LoRa: broadcast packet {nr}: sending at {ts_str}")
    start = time.monotonic()
    if self.transmit(
      f"B,{ts_str},{self._config.LOGGER_ID},{nr},{self.rfm9x.node}",
      ack=True):
      duration = time.monotonic()-start
      g_logger.print(f"LoRa: broadcast: packet {nr}: transfer-time: {duration}s")
    else:
      g_logger.print(f"LoRa: broadcast: packet {nr}: failed")
      return None

    # wait for response
    timeout  = max(1,timeout-duration)
    return self.receive(with_ack=False,timeout=timeout)

  # --- query time   ---------------------------------------------------------

  def get_time(self,retries=3,timeout=10):
    """ send a time-query package """

    for i in range(retries):
       # send packet ("T",node)
       g_logger.print(f"LoRa: sending time-query package, retry={i}")
       start = time.monotonic()
       if self.transmit(f"T,{self.rfm9x.node}",ack=True):
         duration = time.monotonic()-start
         g_logger.print(f"LoRa: time-query {i} sent in {duration}s")
       else:
         g_logger.print(f"LoRa: : time-query {i} failed")
         continue

       # wait for response
       timeout  = max(1,timeout-duration)
       new_time = self.receive(with_ack=False,timeout=timeout)[0]
       if new_time:
         g_logger.print(f"LoRa: : time-query {i} returned {new_time}")
         return int(new_time)
    # query failed!
    g_logger.print(f"LoRa: time-query failed after {retries} retries")
    return None
