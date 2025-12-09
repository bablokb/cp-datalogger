#-----------------------------------------------------------------------------
#  LoRa gateway with Blues cellular. This is the main application class.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import busio
import builtins
import board
from digitalio import DigitalInOut, Direction, Pull
import gc

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

def get_rx_noop():
  """ import and return NoopReceiver class """
  from gw_rx_noop import NoopReceiver
  return NoopReceiver

def get_rx_lora():
  """ import and return LoraReceiver class """
  from gw_rx_lora import LoraReceiver
  return LoraReceiver

def get_tx_blues():
  """ import and return BluesSender class """
  from gw_tx_blues import BluesSender
  return BluesSender

def get_tx_udp():
  """ import and return UDPSender class """
  from gw_tx_udp import UDPSender
  return UDPSender

def get_tx_noop():
  """ import and return NoopSender class """
  from gw_tx_noop import NoopSender
  return NoopSender

RX_MAP = {
  'Noop': get_rx_noop,
  'Lora': get_rx_lora
  }
TX_MAP = {
  'Noop':  get_tx_noop,
  'Blues': get_tx_blues,
  'UDP': get_tx_udp,
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

    self.receiver    = rx_klass(g_config)
    self.transmitter = tx_klass(g_config)

  # --- hardware-setup   -----------------------------------------------------

  def _setup(self):
    """ initialize hardware """

    # hw_helper won't throw an exception, if hardware is not in config
    g_logger.print(f"gateway: initializing")
    self.i2c  = hw_helper.init_i2c(pins,g_config,g_logger)
    self.oled = hw_helper.init_oled(self.i2c,g_config,g_logger)
    self.spi  = hw_helper.init_sd(pins,g_config,g_logger)
    self.rtc  = hw_helper.init_rtc(pins,g_config,self.i2c)

    self.receiver.setup(self.i2c,self.spi)
    self.transmitter.setup(self.i2c,self.spi)
    self._update_time()

    # configure active window
    self._active_until = time.time() + 60*g_config.ON_DURATION
    g_logger.print(
      f"gateway: active until: {self.rtc.print_ts(None,self._active_until)}")

    g_logger.print(f"gateway: initialized")

  # --- query time (internal or from upstream)   -----------------------------

  def _update_time(self):
    """ query time: try internal RTC, then upstream """

    if self.rtc.update():     # (time-server->)ext-rtc->int-rtc
      return

    # try to fetch time from upstream
    ts = self.transmitter.get_time()
    if ts:
      g_logger.print("gateway: updated time from upstream")
      self.rtc.rtc_ext.datetime = ts
    else:
      g_logger.print("gateway: could not set time")

  # --- reply to broadcast-messages   ----------------------------------------

  def _handle_broadcast(self,values):
    """ echo data to sender """

    g_logger.print("gateway: processing broadcast-data...")
    start = time.monotonic()
    rc = self.receiver.handle_broadcast(values)
    duration = time.monotonic()-start

    if self.oled:
      # values is: TS,ID,pnr,node -> fit to max three lines
      self.update_oled([values[0],
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
    rc = self.receiver.handle_time_request(values)
    duration = time.monotonic()-start
    if rc:
      g_logger.print(f"gateway: transmit successful. Duration: {duration}s")
    else:
      g_logger.print(f"gateway: transmit failed. Duration: {duration}s")

  # --- process data   -------------------------------------------------------

  def _process_data(self, values, tasks="TASKS"):
    """ process data """

    if not hasattr(g_config,tasks):
      return

    for task in getattr(g_config,tasks).split(" "):
      try:
        g_logger.print(f"{task}: loading")
        task_module = builtins.__import__("tasks."+task,None,None,["run"],0)
        g_logger.print(f"{task} starting")
        task_module.run(g_config,self,values)
        g_logger.print(f"{task} ended")
      except Exception as ex:
        g_logger.print(f"{task} failed: exception: {ex}")
      task_module = None
      gc.collect()

  # --- update OLED   --------------------------------------------------------

  def update_oled(self,values):
    """ update OLED """

    if not (getattr(g_config,"HAVE_OLED",False) and self.oled):
      return

    display = self.oled.get_display()
    label   = self.oled.get_textlabel()
    lines = 5 if display.height > 32 else 3

    text = "\n".join(values[:min(lines,len(values))])
    if len(values) > lines:
      len_free = 21 - len(values[lines-1]) - 1   # OLED is 21 chars wide
      for i in range(lines,len(values)):
        if len(values[i])+1 > len_free:
          break
        text += f" {values[i]}"
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

    # get start of next active window
    wakeup = self.rtc.get_table_alarm(g_config.TIME_TABLE)
    g_logger.print(
      f"gateway: shutdown until {self.rtc.print_ts(None,wakeup)}")

    # notify sender/receiver to disable power until sleep-time expires
    # Note: calls to shutdown should not return if successful
    try:
      self.transmitter.shutdown(wakeup)
    except Exception as ex:
      g_logger.print(f"gateway: sender.shutdown() failed: {ex}")
    try:
      self.receiver.shutdown(wakeup)
    except Exception as ex2:
      g_logger.print(f"gateway: receiver.shutdown() failed: {ex2}")
    self.rtc.set_alarm(wakeup)
    return self._power_off()

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

    if self.oled:
      self.update_oled([f"{self.rtc.print_ts(None,time.localtime())}",
                         "Waiting for data..."])
    g_logger.print(f"gateway: waiting for incoming data ...")

    while True:
      data = None

      # check for packet
      data = self.receiver.receive_data()
      if data is None:
        # check active time period
        if time.time() > self._active_until:
          g_logger.print("gateway: active time ended: starting shutdown")
          if self._shutdown():
            break
          else:
            g_logger.print("gateway: shutdown failed")
            # try again after another cylce (should actually not happen)
            self._active_until = time.time() + 60*g_config.ON_DURATION
            g_logger.print("gateway: Active until: " +
                           f"{self.rtc.print_ts(None,self._active_until)}")
        continue

      # Decode packet: expect csv data
      try:
        g_logger.print(f"gateway: data received: {data}")
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
