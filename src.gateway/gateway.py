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
from digitalio import DigitalInOut, Direction, Pull

# --- early configuration of the log-destination   ---------------------------

try:
  from log_config import g_logger
except:
  from log_writer import Logger
  g_logger = Logger('console')

import pins
import hw_helper

from settings import Settings
g_config = Settings(g_logger)
g_config.import_config()

# --- small helper functions to create RX and TX classes   -------------------

def get_rx_lora():
  """ import and return LoraReceiver class """
  from gw_rx_lora import LoraReceiver
  return LoraReceiver

def get_tx_blues():
  """ import and return BluesSender class """
  from gw_tx_blues import BluesSender
  return BluesSender

def get_tx_noop():
  """ import and return NoopSender class """
  from gw_tx_noop import NoopSender
  return NoopSender

RX_MAP = {
  'Lora': get_rx_lora
  }
TX_MAP = {
  'Noop':  get_tx_noop,
  'Blues': get_tx_blues
  }

# --- Gateway application class   --------------------------------------------

class Gateway:
  """ main Gateway application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    gw_rx_type = getattr(g_config,'GW_RX_TYPE',"Lora")
    gw_tx_type = getattr(g_config,'GW_TX_TYPE',"Blues")

    try:
      rx_klass = RX_MAP[gw_rx_type]()
    except:
      raise ValueError(f"rx-type '{gw_rx_type}' not implemented!")
    try:
      tx_klass = TX_MAP[gw_tx_type]()
    except:
      raise ValueError(f"tx-type '{gw_tx_type}' not implemented!")

    self._receiver = rx_klass(g_config)
    self._sender   = tx_klass(g_config)

  # --- hardware-setup   -----------------------------------------------------

  def _setup(self):
    """ initialize hardware """

    # hw_helper won't throw an exception, if hardware is not in config
    g_logger.print(f"gateway: initializing")
    self._i2c  = hw_helper.init_i2c(pins,g_config,g_logger)
    self._oled = hw_helper.init_oled(self._i2c,g_config,g_logger)
    self._spi  = hw_helper.init_sd(pins,g_config,g_logger)
    self._rtc  = hw_helper.init_rtc(g_config,self._i2c)

    self._receiver.setup(self._i2c,self._spi)
    self._sender.setup(self._i2c,self._spi)
    self._update_time()

    # configure active window
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

    # query SD-card filename
    if g_config.HAVE_SD:
      ts = time.localtime()
      ymd = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}"
      y,m,d = ymd.split("-")
      self._csv_file = g_config.CSV_FILENAME.format(ID=g_config.LOGGER_ID,
                                           YMD=ymd,Y=y,M=m,D=d)

    g_logger.print(f"gateway: initialized")

  # --- query time (internal or from upstream)   -----------------------------

  def _update_time(self):
    """ query time: try internal RTC, then upstream """

    if self._rtc.update():     # (time-server->)ext-rtc->int-rtc
      return

    # try to fetch time from upstream
    ts = self._sender.get_time()
    if ts:
      g_logger.print("gateway: updated time from upstream")
      self._rtc.rtc_ext.datetime = ts
    else:
      g_logger.print("gateway: could not set time")

  # --- reply to broadcast-messages   ----------------------------------------

  def _handle_broadcast(self,values):
    """ echo data to sender """

    g_logger.print("gateway: processing broadcast-data...")
    start = time.monotonic()
    rc = self._receiver.handle_broadcast(values)
    duration = time.monotonic()-start

    if getattr(g_config,"HAVE_OLED",False) and self._oled:
      # values is: TS,ID,pnr,node -> fit to max three lines
      self._update_oled([values[0],
                         f"ID/N:{values[1]}/{values[3]}: {values[2]}",
                         "OK" if rc else "FAILED"])
    if rc:
      g_logger.print(f"gateway: retransmit successful. Duration: {duration}s")
    else:
      g_logger.print(f"gateway: retransmit failed. Duration: {duration}s")

  # --- reply to query-time-messages   ---------------------------------------

  def _handle_time_request(self,values):
    """ echo data to sender """

    g_logger.print("gateway: processing time-request...")
    start = time.monotonic()
    rc = self._receiver.handle_time_request(values)
    duration = time.monotonic()-start
    if rc:
      g_logger.print(f"gateway: transmit successful. Duration: {duration}s")
    else:
      g_logger.print(f"gateway: transmit failed. Duration: {duration}s")

  # --- process data   -------------------------------------------------------

  def _process_data(self,values):
    """ process data """

    # local processing

    # ...save to SD
    if getattr(g_config,"HAVE_SD",False):
      self._save_data(values)
    # ...show on display
    if getattr(g_config,"HAVE_OLED",False) and self._oled:
      self._update_oled(values)

    # remote processing
    self._sender.process_data(values)

  # --- save data to SD-card   -----------------------------------------------

  def _save_data(self,values):
    """ save data to a SD-card """

    g_logger.print(f"gateway: saving data to {self._csv_file}...")
    with open(self._csv_file, "a") as f:
      f.write(f"{values}\n")

  # --- update OLED   --------------------------------------------------------

  def _update_oled(self,values):
    """ update OLED """

    display = self._oled.get_display()
    label   = self._oled.get_textlabel()
    lines = 5 if display.height > 32 else 3

    text = ""
    for i in range(min(lines,len(values))):
      text += f"{values[i]}\n"

    g_logger.print("gateway: updating OLED...")
    label.text = text

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- shutdown   -----------------------------------------------------------

  def _shutdown(self):
    """ Shutdown system. Shutdown can be controlled by sender, receiver or
    internally.
    """

    # get start of next active window (tomorrow)
    g_logger.print(
      f"gateway: shutdown until tomorrow, {self._start_h:02}:{self._start_m:02}")

    # calculate sleep-time
    tm = self._rtc.datetime
    s_time = ((23-tm.tm_hour)*3600 +
              (59-tm.tm_min)*60 +
              (59-tm.tm_sec) +
              3600*self._start_h + 60*self._start_m)
    g_logger.print(f"gateway: sleep-duration: {s_time}s")

    # in DEV_MODE, only sleep for a short time
    if self._dev_mode:
      uptime_left = getattr(g_config,'DEV_UPTIME',300) - int(
        time.monotonic()-self._startup)
      if uptime_left > 0:
        # ignore to guarantee a minum uptime
        g_logger.print(f"gateway: DEV_MODE: ignoring shutdown for {uptime_left}s")
        return False
      else:
        s_time = getattr(g_config,'DEV_SLEEP',60)
        g_logger.print(f"gateway: DEV_MODE: change sleep-duration to: {s_time}s")

    # notify sender/receiver to disable power until sleep-time expires
    if not (self._sender.shutdown(s_time) or self._receiver.shutdown(s_time)):
      self._set_wakeup(s_time)
      return self._power_off()
    return True

  # --- set next wakeup   ----------------------------------------------------

  def _set_wakeup(self,s_time):
    """ set wakeup time """
    # TODO: implement

  # --- power off   ----------------------------------------------------------

  def _power_off(self):
    """ tell the power-controller to cut power """

    if getattr(g_config,"HAVE_PM",False) and hasattr(pins,"PIN_DONE"):
      g_logger.print("gateway: signal power-off")

      if type(pins.PIN_DONE) == DigitalInOut:
        self.done           = pins.PIN_DONE
      else:
        self.done           = DigitalInOut(pins.PIN_DONE)

      # The following statement is not reliable: even if value is False
      # it might create a short High while switching. This does not
      # matter, "worst case" would be that it already turns of power.
      shutdown_value = getattr(g_config,"SHUTDOWN_HIGH",True)
      self.done.switch_to_output(value=not shutdown_value)

      self.done.value = shutdown_value
      time.sleep(0.001)
      self.done.value = not shutdown_value
      time.sleep(2)
      return True
    else:
      g_logger.print(
        "gateway: ignoring shutdown (don't have PM or PIN_DONE undefined)")
      return False

  # --- main-loop   ----------------------------------------------------------

  def run(self):
    """ application loop """

    g_logger.print("gateway: program start")

    # initialize hardware
    self._setup()

    g_logger.print(f"gateway: waiting for incoming transmissions ...")
    while True:
      data = None

      # check for packet
      data = self._receiver.receive_data()
      if data is None:
        # check active time period
        ts = time.localtime()
        if ts.tm_hour >= self._end_h and ts.tm_min  >= self._end_m:
          if self._shutdown():
            break
        continue

      # Decode packet: expect csv data
      try:
        g_logger.print(f"gateway: data: {data}")
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
        g_logger.print(f"gateway: could not process data: {ex}")
