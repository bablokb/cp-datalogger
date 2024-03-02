#-----------------------------------------------------------------------------
#  LoRa gateway with Blues cellular. This is the main application class.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import busio
import board
import busio
from digitalio import DigitalInOut, Direction, Pull

# --- early configuration of the log-destination   ---------------------------

try:
  from log_config import g_logger
except:
  raise
  from log_writer import Logger
  g_logger = Logger('console')

import config as g_config
from lora import LORA
import pins

# --- imports for Notecard
import notecard
from notecard import hub, card, note, file

# --- Gateway application class   --------------------------------------------

class Gateway:
  """ main Gateway application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """
    pass

  # --- hardware-setup   -----------------------------------------------------

  def _setup(self):
    """ initialize hardware """

    g_logger.print(f"initializing gateway")
    self._i2c  = busio.I2C(sda=pins.PIN_SDA,scl=pins.PIN_SCL)
    self._lora = LORA(g_config)
    self._init_notecard()
    g_logger.print(f"gateway initialized")

  # --- Notecard   -------------------------------------------------------------

  def _init_notecard(self):
    """ initialize Notecard """

    self._card = notecard.OpenI2C(self._i2c,0,0,debug=False)
    hub.set(self._card,mode="minimum")

  # --- process data   -------------------------------------------------------

  def _process_data(self,values):
    """ process data  """

    g_logger.print("processing sensor-data...")
    start = time.monotonic()
    if g_config.SYNC_BLUES_ACTION is not None:
      resp = note.add(self._card,
                      file=f"dl_data.qo",
                      body={"data":','.join(values)},
                      sync=g_config.SYNC_BLUES_ACTION)
    else:
      resp = "action: noop"
    duration = time.monotonic()-start
    g_logger.print(f"action: {g_config.SYNC_BLUES_ACTION}, {resp=}")
    g_logger.print(f"duration: {duration}s")

  # --- reply to broadcast-messages   ----------------------------------------

  def _handle_broadcast(self,values):
    """ echo data to sender """

    g_logger.print("processing broadcast-data...")
    start = time.monotonic()

    resp = f"{values[2]},{self._snr},{self._rssi}"        # 2: packet-nr
    self._lora.set_destination(int(values[3]))            # 3: LoRa-node
    g_logger.print(f"sending '{resp}' to {self._lora.rfm9x.destination}...")
    rc = self._lora.transmit(resp,ack=False,keep_listening=True)
    duration = time.monotonic()-start
    if rc:
      g_logger.print(f"retransmit successful. Duration: {duration}s")
    else:
      g_logger.print(f"retransmit failed. Duration: {duration}s")

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- main-loop   ----------------------------------------------------------

  def run(self):
    """ application loop """

    g_logger.print("gateway program start")

    # initialize hardware
    self._setup()

    g_logger.print(f"waiting for incoming transmissions ...")
    while True:
      data = None

      # check for packet
      data, self._snr, self._rssi = self._lora.receive(
        with_ack=True,timeout=g_config.RECEIVE_TIMEOUT)
      if data is None:
        continue

      # Decode packet: expect csv data
      try:
        g_logger.print(f"data: {data}")
        values = data.split(',')
        if values[0] == 'B':
          broadcast_mode = True
          values.pop(0)
        else:
          broadcast_mode = False

        if broadcast_mode:
          self._handle_broadcast(values)
        else:
          self._process_data(values)
      except Exception as ex:
        g_logger.print(f"could not process data: {ex}")

      # add minimal sleep
      time.sleep(0.05)
