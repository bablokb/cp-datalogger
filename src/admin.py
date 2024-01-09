#-----------------------------------------------------------------------------
# Start admin-mode: run AP together with a web-server.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import wifi
import time
import busio
from digitalio import DigitalInOut, Pull, Direction

import pins
import webap
from datacollector import g_config

from log_writer import Logger
from rtc_ext.pcf8523 import ExtPCF8523 as ExtRTC

# access point settings
try:
  from ap_config import ap_config
except:
  ap_config = {
    'debug': True,
    'cache': False,
    'ssid': 'datalogger',
    'password': '12345678',             # ignored for wifi.AuthMode.OPEN
    'auth_modes': [wifi.AuthMode.OPEN], # or [wifi.AuthMode.WPA2, wifi.AuthMode.PSK]
    'hostname': 'datalogger'           # msdn hostname
  }

# --- turn on LED on sensor-pcb   --------------------------------------------

switch_d = DigitalInOut(pins.PIN_SWD)
switch_d.direction = Direction.OUTPUT
switch_d.value = True

# --- init environment   -----------------------------------------------------

g_logger = Logger()
if g_config.TEST_MODE:
  time.sleep(5)

# --- set CS of display to high   --------------------------------------------

if g_config.HAVE_DISPLAY:
  cs_display = DigitalInOut(pins.PIN_INKY_CS)
  cs_display.switch_to_output(value=True)

# --- read rtc   -------------------------------------------------------------

if g_config.HAVE_PCB:
  try:
    i2c1 = busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)
    rtc = ExtRTC(i2c1)
    rtc.rtc_ext.high_capacitance = True
    rtc.update()
  except Exception as ex:
    g_logger.print(f"could not read RTC: {ex}")
    rtc = None
  ap_config["rtc"] = rtc  # pass to webap for later use

# --- mount sd-card if available   -------------------------------------------

spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
if g_config.HAVE_SD:
  import storage
  import adafruit_sdcard
  sd_cs  = DigitalInOut(pins.PIN_SD_CS)
  sdcard = adafruit_sdcard.SDCard(spi,sd_cs)
  vfs    = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")

# --- put info on display if available   -------------------------------------

if g_config.HAVE_DISPLAY:
  import displayio
  from adafruit_bitmap_font import bitmap_font
  from adafruit_display_text import label as label
  from vectorio import Rectangle
  from display import Display

  g_logger.print("starting display update")
  cs_display.deinit()
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
                        text='Admin-Mode',anchor_point=(0.5,0))
  heading.anchored_position = (display.width/2,0)
  group.append(heading)

  ap_info_text=f"""
  SSID: {ap_config['ssid']}
  PW:   {ap_config['password']}
  URL:  http://192.168.4.1
  """
  ap_info = label.Label(font=font,color=shader[1],
                        tab_replacement=(2," "),
                        line_spacing=1,
                        text=ap_info_text,anchor_point=(0,0))
  ap_info.anchored_position = (0,heading.height+3)
  group.append(ap_info)

  display.root_group = group
  display.refresh()
  g_logger.print("finished display update")

# --- start AP and web-server   ----------------------------------------------

g_logger.print("!!! Starting in ADMIN-Mode !!!")
server = webap.WebAP(config=ap_config)
server.run()
