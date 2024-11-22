#-----------------------------------------------------------------------------
# A gateway receiver using LoRa as RX-technology.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import busio

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()

from lora import LORA
import pins

# --- LoraReceiver class   ------------------------------------------------

class LoraReceiver:
  """ LoraReceiver class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """

    g_logger.print(f"LoraReceiver: initializing hardware")
    if not spi:
      spi = busio.SPI(pins.PIN_LORA_SCK,pins.PIN_LORA_MOSI,
                      pins.PIN_LORA_MISO)
    self._lora = LORA(self._config,spi)

  # --- receive data   -------------------------------------------------------

  def receive_data(self):
    """ receive data """
    data, self._snr, self._rssi = self._lora.receive(
      with_ack=True,timeout=getattr(self._config,"RECEIVE_TIMEOUT",1.0))
    return data

  # --- reply to broadcast-messages   ----------------------------------------

  def handle_broadcast(self,values):
    """ echo data to sender """

    resp = f"{values[2]},{self._snr},{self._rssi}"        # 2: packet-nr
    self._lora.set_destination(int(values[3]))            # 3: LoRa-node
    g_logger.print(f"LoraReceiver: sending '{resp}' to {self._lora.rfm9x.destination}...")
    rc = self._lora.transmit(resp,ack=False,keep_listening=True)
    return rc

  # --- reply to query-time-messages   ---------------------------------------

  def handle_time_request(self,values):
    """ echo data to sender """

    self._lora.set_destination(int(values[0]))
    resp = f"{time.time()}"
    g_logger.print(f"LoraReceiver: sending time ({resp}) to node {self._lora.rfm9x.destination}...")
    rc = self._lora.transmit(resp,ack=False,keep_listening=True)
    return rc

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,s_time):
    """ Shutdown system. In our case, ignore the rquest """

    g_logger.print(f"LoraReceiver: shutdown not implemented")
    return False
