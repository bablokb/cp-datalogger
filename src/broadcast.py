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

# --- check and initialize OLED-display   ------------------------------------


if getattr(g_config,'HAVE_OLED',None):
  try:
    from oled import OLED
    oled_display = OLED(g_config,i2c1)
    width,height = oled_display.get_size()
    g_logger.print(f"OLED created with size {width}x{height}")
  except Exception as ex:
    g_logger.print(f"could not initialize OLED: {ex}")
    oled_display = None

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

# --- loop and send/receive data   -------------------------------------------

lora = LORA(g_config)

broadcast_int = getattr(g_config,'BROADCAST_INT',10)

# query time from gateway and update local time
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

# send broadcast packages
oled_display.clear()
oled_display.show_text(["broadcasting..."])
i = 0
while True:
  i += 1
  start = time.monotonic()
  packet = lora.broadcast(i,timeout=broadcast_int)
  duration = time.monotonic()-start
  if not packet:
    stime = max(0,broadcast_int-duration)
    g_logger.print(f"Broadcast: next cycle in {stime}s...")
    time.sleep(stime)
    continue

  try:
    data,my_snr,my_rssi = packet
    # decode and print/update display
    nr,gw_snr,gw_rssi = data.split(',')
    if int(nr) != i:
      g_logger.print(f"Broadcast: received wrong packet ({nr} but expected {i})")
    else:
      g_logger.print(
        f"Broadcast: packet {i}: SNR(gw), RSSI(gw): {gw_snr}, {gw_rssi}dBm")
      g_logger.print(
        f"Broadcast: packet {i}: SNR(node), RSSI(node): {my_snr}, {my_rssi}dBm")
      g_logger.print(
        f"Broadcast: packet {i}: roundtrip-time: {duration}s")
  except:
    g_logger.print(
        f"Broadcast: packet {i}: wrong data-format: {data}")

  # wait until broadcast-interval is done
  stime = max(0,broadcast_int-duration)
  g_logger.print(f"Broadcast: next cycle in  {stime}s...")
  time.sleep(stime)
