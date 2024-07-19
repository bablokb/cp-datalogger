#-----------------------------------------------------------------------------
# Start broadcast-mode: run LoRa communication to optimize antenna setup
#
# Broadcast-data is in CSV-format:
#     B,<ts>,<id>,<nr>,<node>
# with a fixed "B", followed by the timestamp, logger-id, packet-number
# and LoRa-node-id.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import board
import wifi
import time
import busio
from digitalio import DigitalInOut, Pull, Direction

import displayio
displayio.release_displays()

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label as label
from vectorio import Rectangle

import pins
from datacollector import g_config
from lora import LORA
from log_writer import Logger
from rtc_ext.pcf8523 import ExtPCF8523 as ExtRTC
from sleep import TimeSleep

# --- init environment   -----------------------------------------------------

if hasattr(pins,"PIN_SWD"):
  switch_d = DigitalInOut(pins.PIN_SWD)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True
elif hasattr(board,'LED'):
  switch_d = DigitalInOut(board.LED)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True

g_logger = Logger()
if g_config.TEST_MODE:
  TimeSleep.light_sleep(duration=5)
g_logger.print("!!! Starting in Broadcast-Mode !!!")

# --- application class for broadcast-mode   ---------------------------------

class Broadcast:
  """ main application class for broadcast-mode """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """
    self._display = None
    self._lines   = [""]*5
    self._pnr     = 0
    self._pok     = 0
    self._lora    = LORA(g_config)

    self._init_rtc()
    self._init_display()
    self._have_oled = self._init_oled()
    if self._have_oled or not self._display:
      self.interval = getattr(g_config,'BROADCAST_INT',10)
    else:
      # set update-interval to at least 60 seconds to protect display
      self.interval = max(getattr(g_config,'BROADCAST_INT',10),60)
      self._last_ref = 0

  # --- read rtc   -----------------------------------------------------------

  def _init_rtc(self):
    """ initialize RTC """
    self._i2c1 = None
    if g_config.HAVE_RTC:
      rtc_bus = int(g_config.HAVE_RTC.split('(')[1][0])
      try:
        if rtc_bus == 1:
          i2c = busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)
        else:
          i2c = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
        self._rtc = ExtRTC(i2c)
        self._rtc.rtc_ext.high_capacitance = True
        self._rtc.update()
      except Exception as ex:
        g_logger.print(f"could not read RTC: {ex}")
        self._rtc = None

  # --- standard display   -------------------------------------------------

  def _init_display(self):
    """ initialize standard display """

    if g_config.HAVE_DISPLAY:
      from display import Display

      g_logger.print("starting display update")
      spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
      self._display = Display(g_config,spi).get_display()

      font = bitmap_font.load_font(f"fonts/{g_config.FONT_DISPLAY}.bdf")
      group = displayio.Group()
      shader = displayio.Palette(2)
      shader[0] = 0xFFFFFF
      shader[1] = 0x000000
      group.append(Rectangle(pixel_shader=shader,x=0,y=0,
                             width=self._display.width,
                             height=self._display.height,
                             color_index=0))
      heading = label.Label(font=font,color=shader[1],scale=2,
                            text='Broadcast-Mode',anchor_point=(0.5,0))
      heading.anchored_position = (self._display.width/2,0)
      group.append(heading)

      self._textlabel = label.Label(font=font,color=shader[1],scale=1,
                                    text="",line_spacing=1.0,
                                    anchor_point=(0,0))
      self._textlabel.anchored_position = (2,heading.height+15)
      group.append(self._textlabel)

      self._display.root_group = group
      self._display.refresh()
      self._last_ref = time.monotonic()
      g_logger.print("finished display update")

  # --- OLED display   -------------------------------------------------------
  # NOTE: the main display will receive no more updates once this is setup

  def _init_oled(self):
    """ init OLED display """

    if getattr(g_config,'HAVE_OLED',None):
      try:
        from oled import OLED
        displayio.release_displays()
        oled_display    = OLED(g_config,self._i2c1,None)
        self._display   = oled_display.get_display()
        self._textlabel = oled_display.get_textlabel()
        g_logger.print(
          f"OLED created with size {self._display.width}x{self._display.height}")
        return True
      except Exception as ex:
        g_logger.print(f"could not initialize OLED: {ex}")
    return False

  # --- update info   --------------------------------------------------------

  def update_info(self,lines,row=0):
    """ update info-text """

    for line in lines:
      if row >= len(self._lines):
        break
      self._lines[row] = line
      row += 1

  # --- update display   -----------------------------------------------------

  def update_display(self):
    """ update display """
    if self._display:
      self._textlabel.text = "\n".join(self._lines)
      if not self._have_oled:
        # refresh only once per minute
        wait_for_ref = max(0,60-(time.monotonic()-self._last_ref))
        g_logger.print(f"waiting {wait_for_ref}s for display refresh")
        TimeSleep.light_sleep(duration=max(0,60-(time.monotonic()-self._last_ref)))
        self._last_ref = time.monotonic()
      g_logger.print(f"refreshing display")
      self._display.refresh()
      if not self._have_oled:
        time.sleep(3)             # e-ink needs some additional time

  # --- clear display   ------------------------------------------------------

  def clear(self):
    """ clear display """
    self._lines = [""]*len(self._lines)
    if self._display:
      self._textlabel.text = ""
      if self._have_oled:
        self._display.refresh()

  # --- update time   --------------------------------------------------------

  def update_time(self):
    """ update time """

    self.update_info(["Updating time..."])
    new_time = self._lora.get_time(timeout=3)
    if new_time:
      g_logger.print(f"Broadcast: updating device-time from gateway-time")
      self._rtc.update(new_time)
      self.update_info(["... ok!",ExtRTC.print_ts(None,new_time)],
                       row=1)
    else:
      self.update_info(["... failed!"],row=1)
    self.update_display()

  # --- send broadcast-packet   ----------------------------------------------

  def send_packet(self):
    """ send broadcast packet """

    self._pnr += 1

    # update time on display (will not show on 128x32)
    self.update_info([ExtRTC.print_ts(None,time.localtime())],row=4)

    # send packet and receive response
    start = time.monotonic()
    packet = self._lora.broadcast(self._pnr,timeout=self.interval)
    duration = time.monotonic()-start
    if not packet:
      return

    # try to decode packet
    try:
      data,my_snr,my_rssi = packet
      nr,gw_snr,gw_rssi = data.split(',')
      nr      = int(nr)
      gw_snr  = round(float(gw_snr),1)
      gw_rssi = int(gw_rssi)
    except Exception as ex:
      g_logger.print(
          f"Broadcast: packet {self._pnr}: wrong data-format: {data}")
      nr = 0    # will trigger failed-message

    # check packet
    try:
      if nr != self._pnr:
        g_logger.print(
          f"Broadcast: received wrong packet ({nr} but expected {self._pnr})")
        self.update_info([f"packet {self._pnr} failed!",
                          f"count: {self._pok}/{self._pnr} ok",
                          f"RTT: {duration}s"],row=1)
      else:
        self._pok += 1
        g_logger.print(
          f"Broadcast: packet {self._pnr}: SNR(gw), RSSI(gw): {gw_snr:0.1f}, {gw_rssi}dBm")
        g_logger.print(
          f"Broadcast: packet {self._pnr}: SNR(node), RSSI(node): {my_snr:0.1f}, {my_rssi}dBm")
        g_logger.print(
          f"Broadcast: packet {self._pnr}: roundtrip-time: {duration}s")
        self.update_info([f"SNR: {gw_snr:0.1f},RSSI:{gw_rssi}dBm",
                          f"count: {self._pok}/{self._pnr} ok",
                          f"RTT: {duration}s"],row=1)
    except Exception as ex:
      g_logger.print(f"excepion: {ex}")   # not expected
    return

# --- main program start   ---------------------------------------------------

app = Broadcast()
app.update_time()
TimeSleep.light_sleep(duration=5)

app.clear()
app.update_info([f"Node: {g_config.LORA_NODE_ADDR}, ID: {g_config.LOGGER_ID}"])

while True:
  start = time.monotonic()
  app.send_packet()
  app.update_display()
  stime = max(0,app.interval - (time.monotonic()-start))
  g_logger.print(f"Broadcast: next cycle in  {stime}s...")
  TimeSleep.light_sleep(duration=stime)
