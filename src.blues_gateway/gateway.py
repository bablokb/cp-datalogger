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
import rtc
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
    self._init_rtc()

    start = getattr(g_config,'ACTIVE_WINDOW_START',"7:00").split(':')
    self._start_h = int(start[0])
    self._start_m = int(start[1])
    end = getattr(g_config,'ACTIVE_WINDOW_END',"17:00").split(':')
    self._end_h = int(end[0])
    self._end_m = int(end[1])
    g_logger.print(
      f"Active Window: {self._start_h:02}:{self._start_m:02}-{self._end_h:02}:{self._end_m:02}")

    self._dev_mode = getattr(g_config,'DEV_MODE',False)
    if self._dev_mode:
      self._startup = time.monotonic()
    g_logger.print(f"gateway initialized")

  # --- Notecard   -----------------------------------------------------------

  def _init_notecard(self):
    """ initialize Notecard """

    self._card = notecard.OpenI2C(self._i2c,0,0,debug=False)
    hub.set(self._card,mode="minimum")

    # query start-mode (timer or manual)
    resp = card.attn(self._card,mode="")
    self._is_timer_start = 'files' in resp and 'timeout' in resp['files']
    g_logger.print(f"start in timer-mode: {self._is_timer_start}")
    # disarm attn
    resp = card.attn(self._card,mode="disarm")

  # --- initialize on-board RTC   --------------------------------------------

  def _init_rtc(self):
    """ initialize RTC """

    self._rtc = rtc.RTC()
    i = 0
    while i < 2:
      i += 1
      g_logger.print("trying to set time from notecard...")
      resp = card.time(self._card)
      if 'time' in resp:
        ts = time.localtime(resp['time'] + 60*resp['minutes'])
        self._rtc.datetime = ts
        return True
      else:
        g_logger.print(f"time not available, wating for sync")
        if not self._sync_notecard():
          g_logger.print("could not set time")
          return False

  # --- sync notecard   ------------------------------------------------------

  def _sync_notecard(self,wait=True):
    """ sync notecard """

    resp = hub.sync(self._card)
    if not wait:
      return False
    max_sync_time = getattr(g_config,'MAX_SYNC_TIME',300)
    resp = hub.syncStatus(self._card)
    while "requested" in resp:
      requested = resp['requested']
      g_logger.print(f"sync request in progress since {requested}s")
      if requested > max_sync_time:
        g_logger.print(f"could not sync within {max_sync_time}s")
        return False
      time.sleep(10)
      resp = hub.syncStatus(self._card)
    return True

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

  # --- reply to query-time-messages   ---------------------------------------

  def _handle_time_request(self,values):
    """ echo data to sender """

    g_logger.print("processing time-request...")
    start = time.monotonic()

    self._lora.set_destination(int(values[0]))
    resp = f"{time.time()}"
    g_logger.print(f"sending time ({resp}) to node {self._lora.rfm9x.destination}...")
    rc = self._lora.transmit(resp,
                             ack=False,keep_listening=True)
    duration = time.monotonic()-start
    if rc:
      g_logger.print(f"transmit successful. Duration: {duration}s")
    else:
      g_logger.print(f"transmit failed. Duration: {duration}s")

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- shutdown   -----------------------------------------------------------

  def _shutdown(self):
    """ signal attn to notecard to cut power and set wakeup """

    # get start of next active window (tomorrow)
    g_logger.print(
      f"shutdown until tomorrow, {self._start_h:02}:{self._start_m:02}")

    # calculate sleep-time
    tm = self._rtc.datetime
    s_time = ((23-tm.tm_hour)*3600 +
              (59-tm.tm_min)*60 +
              (59-tm.tm_sec) +
              3600*self._start_h + 60*self._start_m)
    g_logger.print(f"sleep-duration: {s_time}s")

    # in DEV_MODE, only sleep for a short time
    if self._dev_mode:
      uptime_left = getattr(g_config,'DEV_UPTIME',300) - int(
        time.monotonic()-self._startup)
      if uptime_left > 0:
        # ignore to guarantee a minum uptime
        g_logger.print(f"DEV_MODE: ignoring shutdown for {uptime_left}s")
        return False
      else:
        s_time = getattr(g_config,'DEV_SLEEP',60)
        g_logger.print(f"DEV_MODE: change sleep-duration to: {s_time}s")

    # notify card to disable power until sleep-time expires
    g_logger.print(f"executing card.attn() with seconds={s_time}s")
    card.attn(self._card,mode="sleep",seconds=s_time)
    time.sleep(10)
    return True

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
        # check active time period
        if (self._rtc.datetime.tm_hour >= self._end_h and
            self._rtc.datetime.tm_min  >= self._end_m):
          # if necessary, sync notes before shutdown
          if g_config.SYNC_BLUES_ACTION == False:
            self._sync_notecard(wait=False)
          if self._shutdown():
            break
        continue

      # Decode packet: expect csv data
      try:
        g_logger.print(f"data: {data}")
        values = data.split(',')
        if values[0] in ['B', 'T']:
          mode = values[0]
          values.pop(0)
        else:
          mode = 'N'

        if mode == 'B':
          self._handle_broadcast(values)
        elif mode == 'T':
          self._handle_time_request(values)
        else:
          self._process_data(values)
      except Exception as ex:
        g_logger.print(f"could not process data: {ex}")

