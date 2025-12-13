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
import time
import adafruit_rfm9x
import pins

# --- quality of service settings   ------------------------------------------

# tuple of spreading-factor, coding-rate, signal-bandwidth
# Time per symbol is T(s) = 2**SF/BW
_LORA_QOS = [
  ( 7, 5, 125000),      # 0
  ( 7, 7, 125000),      # 1
  ( 8, 7, 125000),      # 2
  ( 9, 7, 125000),      # 3, default
  (10, 5, 125000),      # 4
  (11, 5, 125000),      # 5
  (11, 8, 125000),      # 6
  (12, 6, 125000),      # 7
  ]
_LORA_QOS_DEF = 3  # 0 is library default

# --- helper class for LoRa   ------------------------------------------------

@singleton
class LORA:
  def __init__(self,config,spi):
    """ constructor """

    # Calling the constructor with None will return the singleton, if it
    # exists. If not, bail out: the app has to retry and provide all arguments.
    if config is None:
      raise ValueError("config is None")

    self._config = config
    self._trace = getattr(config,'LORA_TRACE',False)

    # technical settings (QOS-setting with possible overrides)
    qos  = getattr(config, 'LORA_QOS', _LORA_QOS_DEF)
    sf   = getattr(config, 'LORA_SF', _LORA_QOS[qos][0])
    cr   = getattr(config, 'LORA_CR', _LORA_QOS[qos][1])
    bw   = getattr(config, 'LORA_BW', _LORA_QOS[qos][2])
    tfac = (1<<(sf-7))*(125000/bw)
    g_logger.print(f"LoRa: QOS-parameter: {(sf,cr,bw)}, t-factor: {tfac}")

    # calculate wait-time/timeout according to tfac
    rtimeout = tfac * getattr(config,'LORA_RECEIVE_TIMEOUT',1.0)
    g_logger.print(f"LoRa: timeout:  {rtimeout:5.2f}s")

    if hasattr(pins,'PIN_LORA_EN'):
      g_logger.print("LoRa: enabling rfm9x")
      pin_enable = DigitalInOut(pins.PIN_LORA_EN)
      pin_enable.direction  = Direction.OUTPUT
      pin_enable.value = 1
      time.sleep(getattr(config,'LORA_ENABLE_TIME',0))

    g_logger.print("LoRa: initializing rfm9x")
    pin_cs     = DigitalInOut(pins.PIN_LORA_CS)
    pin_reset  = DigitalInOut(pins.PIN_LORA_RST)
    self.rfm9x = adafruit_rfm9x.RFM9x(
      spi, pin_cs,pin_reset,config.LORA_FREQ,baudrate=100000)

    g_logger.print("LoRa: configuring rfm9x")
    self.rfm9x.spreading_factor = sf
    self.rfm9x.coding_rate      = cr
    self.rfm9x.signal_bandwidth = bw
    if (cr/4)* 1000 / (bw/(1 << sf)) > 16:
      self.rfm9x.low_datarate_optimize = 1
    else:
      self.rfm9x.low_datarate_optimize = 0

    self.rfm9x.enable_crc = True
    self.rfm9x.receive_timeout = rtimeout
    self.rfm9x.xmit_timeout = rtimeout
    self.rfm9x.tx_power = getattr(config,"LORA_TX_POWER",13)
    self.rfm9x.node = config.LORA_NODE_ADDR                      # this
    self.rfm9x.destination = getattr(config,"LORA_BASE_ADDR",0)  # gateway
    self.rfm9x.sleep()

  # --- trace LoRa-events   --------------------------------------------------

  def trace(self,msg):
    """ trace LoRa events """
    if self._trace:
      g_logger.print(msg)

  # --- transmit command   ---------------------------------------------------

  def transmit(self,string,msg_type=None,keep_listening=False):
    """ send data """
    if msg_type:
      payload = f"{msg_type},{string}"
    else:
      payload = string
    if self._trace:
      g_logger.print(f"LoRa: sending data: {payload}")
      start = time.monotonic()
    rc = self.rfm9x.send(bytes(payload, "UTF-8"),keep_listening=keep_listening)
    if self._trace:
      g_logger.print(f"LoRa:   elapsed: {time.monotonic()-start:0.3f}s")
    return rc

  # --- receive command   ----------------------------------------------------

  def receive(self, keep_listening=True):
    """ receive and decode data """
    if self._trace:
      g_logger.print("LoRa: receiving data...")
      start = time.monotonic()
    packet = self.rfm9x.receive(with_header=True, keep_listening=keep_listening)
    if self._trace:
      g_logger.print(f"LoRa:   elapsed: {time.monotonic()-start:0.3f}s")
    if packet is None:
      self.trace(f"LoRa: no packet within {self.rfm9x.receive_timeout:5.2}s")
      return (None,None,None,None)
    else:
      header  = packet[:4]
      payload = packet[4:].decode()
      self.trace(f"LoRa: header: {header}")
      self.trace(f"LoRa: payload: {payload}")
      return (payload,int(header[1]),self.rfm9x.last_snr,self.rfm9x.last_rssi)

  # --- set destination   ----------------------------------------------------

  def set_destination(self,dest):
    """ set destination for transmit """
    self.rfm9x.destination = dest

  # --- broadcast a packet and wait for response   ---------------------------

  def broadcast(self,nr):
    """ send a broadcast packet """

    ts = time.localtime()
    ts_str = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}T{ts.tm_hour:02d}:{ts.tm_min:02d}:{ts.tm_sec:02d}"

    # send packet ("B",TS,ID,nr,node)
    g_logger.print(f"LoRa: broadcast packet {nr}: sending at {ts_str}")
    start = time.monotonic()
    if self.transmit(
      f"{ts_str},{self._config.LOGGER_ID},{nr},{self.rfm9x.node}", msg_type="B",
      keep_listening=True):
      duration = time.monotonic()-start
      g_logger.print(f"LoRa: broadcast: packet {nr}: transfer-time: {duration}s")
    else:
      g_logger.print(f"LoRa: broadcast: packet {nr}: failed")
      return None

    # wait for response
    return self.receive(keep_listening=False)

  # --- query time   ---------------------------------------------------------

  def get_time(self,retries=3):
    """ send a time-query packet """

    for i in range(retries):
       # send packet ("T",node)
       g_logger.print(f"LoRa: sending time-query packet, retry={i}")
       start = time.monotonic()
       if self.transmit(f"{self.rfm9x.node}", msg_type="T", keep_listening=True):
         duration = time.monotonic()-start
         g_logger.print(f"LoRa: time-query {i} sent in {duration}s")
       else:
         g_logger.print(f"LoRa: : time-query {i} failed")
         continue

       # wait for response
       new_time = self.receive(keep_listening=False)[0]
       if new_time:
         g_logger.print(f"LoRa: : time-query {i} returned {new_time}")
         return int(new_time)
    # query failed!
    g_logger.print(f"LoRa: time-query failed after {retries} retries")
    return None
