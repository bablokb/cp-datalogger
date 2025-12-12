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
    if gettattr(self._config,"DEV_MODE",False):
      self._config_notecard({
        "io": {"req":"card.io","mode":"+busy"}, # LED on/off in wake/sleep state
        })
    else:
      self._config_notecard({
        "io": {"req":"card.io","mode":"+dark"}, # LED on/off in wake/sleep state
        })
    self._config_notecard({
      "transport": {"req": "card.transport", "method": "cell"}, # cell only
      })

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

  # --- configure notecard   -------------------------------------------------

  def _config_notecard(self,settings):
    """ execute configuration requests """

    for req in settings.values():
      try:
        g_logger.print(f"BluesSender: changing setting: {req}")
        self._card.Transaction(req)
      except Exception as ex:
        g_logger.print(f"BluesSender: request for {req} failed: {ex}")

  # --- sync notecard   ------------------------------------------------------

  def _sync_notecard(self,wait=True):
    """ sync notecard """

    g_logger.print("BluesSender: syncing card")
    resp = hub.sync(self._card)
    if not wait:
      return False
    max_sync_time = getattr(self._config,'BLUES_MAX_SYNC_TIME',300)
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
    while i < getattr(self._config,'BLUES_GET_TIME_RETRIES',3):
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

  def process_data(self, msg_type, values):
    """ process data  """

    g_logger.print("processing sensor-data...")
    start = time.monotonic()
    if self._config.BLUES_SYNC_ACTION is not None:
      resp = note.add(self._card,
                      file=f"dl_data.qo",
                      body={"data":','.join(values)},
                      sync=self._config.BLUES_SYNC_ACTION)
    else:
      resp = "action: noop"
    duration = time.monotonic()-start
    g_logger.print(f"BluesSender: action: {self._config.BLUES_SYNC_ACTION}, {resp=}")
    g_logger.print(f"BluesSender: duration: {duration}s")

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system. In our case, send an attn-request to the notecard """

    # if necessary, sync notes before shutdown
    if self._config.BLUES_SYNC_ACTION == False:
      self._sync_notecard(wait=False)

    # turn off some settings
    self._config_notecard({
      "hub":      {"req":"hub.set","mode":"off"},
      "motion":   {"req":"card.motion.mode","stop":True},
      "location": {"req":"card.location.mode","mode":"off"},
      # "aux": {"req":"card.aux","mode":"off"},     # no effect
      # "sleep": {"req":"card.sleep","on":True},    # Notecard Wifi v2 only
      "io": {"req":"card.io","mode":"+busy"},       # LED on/off in wake/sleep state
      })

    #calculate sleep-time
    s_time = time.mktime(wakeup) - time.time()
    g_logger.print(f"BluesSender: executing card.attn() with seconds={s_time}s")
    card.attn(self._card,mode="sleep",seconds=s_time)
    time.sleep(10)
    return True
