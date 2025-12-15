#-----------------------------------------------------------------------------
# A gateway receiver using LoRa as RX-technology.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import atexit
import time
import busio

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()

from lora import LORA
import pins

# --- atexit processing   ----------------------------------------------------

def at_exit(spi):
  """ release spi """
  try:
    # may fail if we want to log to SD
    g_logger.print(f"releasing {spi}")
  except:
    print(f"releasing {spi}")
  spi.deinit()

# --- LoraReceiver class   ------------------------------------------------

class LoraReceiver:
  """ LoraReceiver class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config
    self._timeout = getattr(config,'LORA_GW_RECEIVE_TIMEOUT',1.0)

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """

    g_logger.print(f"LoraReceiver: initializing hardware")
    if not spi:
      spi = busio.SPI(pins.PIN_LORA_SCK,pins.PIN_LORA_MOSI,
                      pins.PIN_LORA_MISO)
    atexit.register(at_exit,spi)
    self._lora = LORA(self._config,spi)

  # --- receive data   -------------------------------------------------------

  def receive_data(self):
    """ receive data """
    data, node_sender, self._snr, self._rssi = (
      self._lora.receive(timeout=self._timeout))
    if self._snr:
      self._snr = round(self._snr,1)
      self._rssi = round(self._rssi,0)
    return (data, node_sender)

  # --- reply to broadcast-messages   ----------------------------------------

  def handle_broadcast(self,values, node_sender):
    """ echo data to sender """

    # echo data to sender
    resp = f"{values[2]},{self._snr},{self._rssi}"        # 2: packet-nr
    self._lora.set_destination(int(values[3]))            # 3: LoRa-node
    g_logger.print(f"LoraReceiver: sending '{resp}' to {self._lora.rfm9x.destination}...")
    rc = self._lora.transmit(resp,keep_listening=True)
    g_logger.print(f"LoraReceiver: rc: {rc}")
    # update values for further processing: add rc, snr, rssi and
    # technical settings
    values.extend([str(val) for val in [int(rc), self._snr, self._rssi,
                                        self._lora.rfm9x.spreading_factor,
                                        self._lora.rfm9x.coding_rate,
                                        self._lora.rfm9x.signal_bandwidth]])
    return rc

  # --- reply to query-time-messages   ---------------------------------------

  def handle_time_request(self,values, node_sender):
    """ echo data to sender """

    self._lora.set_destination(int(values[0]))
    resp = f"{time.time()}"
    g_logger.print(f"LoraReceiver: sending time ({resp}) to node {self._lora.rfm9x.destination}...")
    rc = self._lora.transmit(resp,keep_listening=True)
    return rc

  # --- reply to data messages   ---------------------------------------------

  def handle_data(self, msg_type, values, node_sender):
    """ process data messages """

    if msg_type == "S":
      self._lora.set_destination(node_sender)
      resp = f"{len(','.join(values))}"
      g_logger.print(f"LoraReceiver: S-msg: returning content length: {resp}")
      rc = self._lora.transmit(resp,keep_listening=True)
      return rc
    else:
      raise RuntimeError(f"unsupported msg-type {msg_type}")

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system. In our case, ignore the request """

    g_logger.print(f"LoraReceiver: ignoring shutdown-request")
    return False
