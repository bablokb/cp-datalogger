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

# --- turn on LED on sensor-pcb   --------------------------------------------

switch_d = DigitalInOut(pins.PIN_SWD)
switch_d.direction = Direction.OUTPUT
switch_d.value = True

# --- init environment   -----------------------------------------------------

g_logger = Logger()
if g_config.TEST_MODE:
  time.sleep(5)
g_logger.print("!!! Starting in Broadcast-Mode !!!")

# --- set CS of display to high   --------------------------------------------

if g_config.HAVE_DISPLAY:
  cs_display = DigitalInOut(pins.PIN_INKY_CS)
  cs_display.switch_to_output(value=True)

# --- read rtc   -------------------------------------------------------------

i2c1 = None
if g_config.HAVE_PCB:
  try:
    i2c1 = busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)
    rtc = ExtRTC(i2c1)
    rtc.rtc_ext.high_capacitance = True
    rtc.update()
  except Exception as ex:
    g_logger.print(f"could not read RTC: {ex}")
    rtc = None

# --- put info on display if available   -------------------------------------

if g_config.HAVE_DISPLAY:
  from display import Display

  g_logger.print("starting display update")
  cs_display.deinit()
  spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
  display = Display(g_config,spi).get_display()

  font = bitmap_font.load_font(f"fonts/{g_config.FONT_DISPLAY}.bdf")
  group = displayio.Group()
  shader = displayio.Palette(2)
  shader[0] = 0xFFFFFF
  shader[1] = 0x000000
  group.append(Rectangle(pixel_shader=shader,x=0,y=0,
                         width=display.width,
                         height=display.height,
                         color_index=0))
  heading = label.Label(font=font,color=shader[1],scale=2,
                        text='Broadcast-Mode',anchor_point=(0.5,0))
  heading.anchored_position = (display.width/2,0)
  group.append(heading)

  display.root_group = group
  display.refresh()
  g_logger.print("finished display update")

# --- check and initialize OLED-display   ------------------------------------

# NOTE: the main display will receive no more updates once this is setup
if getattr(g_config,'HAVE_OLED',None):
  try:
    from oled import OLED
    displayio.release_displays()
    oled_display = OLED(g_config,i2c1)
    oled_width,oled_height = oled_display.get_size()
    g_logger.print(f"OLED created with size {oled_width}x{oled_height}")
  except Exception as ex:
    g_logger.print(f"could not initialize OLED: {ex}")
    oled_display = None
else:
  oled_display = None

# --- update time   ----------------------------------------------------------

lora = LORA(g_config)

# query time from gateway and update local time
if oled_display:
  oled_display.show_text(["Updating time..."])
new_time = lora.get_time(timeout=3)
if new_time:
  g_logger.print(f"Broadcast: updating device-time from gateway-time")
  rtc.update(new_time)
  if oled_display:
    oled_display.show_text(["... ok!",ExtRTC.print_ts(None,new_time)],
                           row=1)
else:
  if oled_display:
    oled_display.show_text(["... failed!"],row=1)

time.sleep(5)

# --- loop and send/receive data   -------------------------------------------

if oled_display:
  oled_display.clear()
  oled_display.show_text(
    [f"Node: {g_config.LORA_NODE_ADDR}, ID: {g_config.LOGGER_ID}"])

interval = getattr(g_config,'BROADCAST_INT',10)
pnr = 0
p_ok = 0
while True:
  pnr += 1

  # update time on larger OLED-displays
  if oled_display:
    oled_display.show_text([ExtRTC.print_ts(None,time.localtime())],row=4)

  start = time.monotonic()
  packet = lora.broadcast(pnr,timeout=interval)
  duration = time.monotonic()-start
  if not packet:
    stime = max(0,interval-duration)
    g_logger.print(f"Broadcast: next cycle in {stime}s...")
    time.sleep(stime)
    continue

  try:
    data,my_snr,my_rssi = packet
    # decode and print/update display
    nr,gw_snr,gw_rssi = data.split(',')
    nr      = int(nr)
    gw_snr  = round(float(gw_snr),1)
    gw_rssi = int(gw_rssi)
  except Exception as ex:
    g_logger.print(
        f"Broadcast: packet {pnr}: wrong data-format: {data}")
    nr = 0

  try:
    if nr != pnr:
      g_logger.print(f"Broadcast: received wrong packet ({nr} but expected {pnr})")
      if oled_display:
        oled_display.show_text([f"packet {pnr} failed!",
                                f"count: {p_ok}/{pnr} ok",
                                f"RTT: {duration}s"],row=1)
    else:
      p_ok += 1
      g_logger.print(
        f"Broadcast: packet {pnr}: SNR(gw), RSSI(gw): {gw_snr:0.1f}, {gw_rssi}dBm")
      g_logger.print(
        f"Broadcast: packet {pnr}: SNR(node), RSSI(node): {my_snr:0.1f}, {my_rssi}dBm")
      g_logger.print(
        f"Broadcast: packet {pnr}: roundtrip-time: {duration}s")
      if oled_display:
        oled_display.show_text([f"SNR: {gw_snr:0.1f},RSSI:{gw_rssi}dBm",
                                f"count: {p_ok}/{pnr} ok",
                                f"RTT: {duration}s"],row=1)
  except Exception as ex:
    g_logger.print(f"excepion: {ex}")

  # wait until broadcast-interval is done
  stime = max(0,interval-duration)
  g_logger.print(f"Broadcast: next cycle in  {stime}s...")
  time.sleep(stime)
