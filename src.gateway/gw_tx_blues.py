#-----------------------------------------------------------------------------
# GatewaySender subclass using Blues.io as TX-technology.
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

import pins

import notecard
from notecard import hub, card, note, file

# --- BluesSender class   ----------------------------------------------------

class BluesSender:
  """ BluesSender class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """

    g_logger.print(f"BluesSender: initializing hardware")
    bus_id = 0 if i2c[0] is not None else 1
    self._i2c = i2c[bus_id]
    g_logger.print(f"BluesSender: using I2C{bus_id} for Blues")
    self._init_notecard()

  # --- Notecard   -----------------------------------------------------------

  def _init_notecard(self):
    """ initialize Notecard """

    self._card = notecard.OpenI2C(self._i2c,0,0,debug=False)
    hub.set(self._card,mode="minimum")

    # query start-mode (timer or manual)
    resp = card.attn(self._card,mode="")
    self._is_timer_start = 'files' in resp and 'timeout' in resp['files']
    g_logger.print(f"BluesSender: start in timer-mode?: {self._is_timer_start}")
    # disarm attn
    resp = card.attn(self._card,mode="disarm")

  # --- sync notecard   ------------------------------------------------------

  def _sync_notecard(self,wait=True):
    """ sync notecard """

    g_logger.print("BluesSender: syncing card")
    resp = hub.sync(self._card)
    if not wait:
      return False
    max_sync_time = getattr(self._config,'MAX_SYNC_TIME',300)
    resp = hub.syncStatus(self._card)
    while "requested" in resp:
      requested = resp['requested']
      g_logger.print(f"BluesSender: sync request in progress since {requested}s")
      if requested > max_sync_time:
        g_logger.print(f"BluesSender: could not sync within {max_sync_time}s")
        return False
      time.sleep(10)
      resp = hub.syncStatus(self._card)
    return True

  # --- get time from upstream   ---------------------------------------------

  def get_time(self):
    """ query time: return time-stamp or None """

    i = 0
    while i < 2:
      i += 1
      g_logger.print("BluesSender: trying to get time from notecard...")
      resp = card.time(self._card)
      if 'time' in resp:
        return time.localtime(resp['time'] + 60*resp['minutes'])
      else:
        g_logger.print(f"BluesSender: time not available, wating for sync")
        if not self._sync_notecard():
          g_logger.print("BluesSender: could not set time")
          return None

  # --- process data   -------------------------------------------------------

  def process_data(self,values):
    """ process data  """

    g_logger.print("processing sensor-data...")
    start = time.monotonic()
    if self._config.SYNC_BLUES_ACTION is not None:
      resp = note.add(self._card,
                      file=f"dl_data.qo",
                      body={"data":','.join(values)},
                      sync=self._config.SYNC_BLUES_ACTION)
    else:
      resp = "action: noop"
    duration = time.monotonic()-start
    g_logger.print(f"BluesSender: action: {self._config.SYNC_BLUES_ACTION}, {resp=}")
    g_logger.print(f"BluesSender: duration: {duration}s")

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system. In our case, send an attn-request to the notecard """

    # if necessary, sync notes before shutdown
    if self._config.SYNC_BLUES_ACTION == False:
      g_logger.print("BluesSender: faking final sync")
      #self._sync_notecard(wait=False)

    #calculate sleep-time
    s_time = time.mktime(wakeup) - time.time()
    g_logger.print(f"BluesSender: executing card.attn() with seconds={s_time}s")
    card.attn(self._card,mode="sleep",seconds=s_time)
    time.sleep(10)
    return True
