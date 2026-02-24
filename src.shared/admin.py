#-----------------------------------------------------------------------------
# Start admin-mode: run AP together with a web-server.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import wifi
import time
import gc
import board
from digitalio import DigitalInOut, Pull, Direction

try:
  from log_config import g_logger
except:
  from log_writer import Logger
  g_logger = Logger('console')

import webap
import hw_helper
import pins

from settings import Settings
g_config = Settings(g_logger)
g_config.import_config()

# access point settings
try:
  from ap_config import ap_config
except:
  ap_config = {
    'debug': False,
    'cache': True,
    'ssid': 'datalogger',
    'password': '12345678',                     # ignored for wifi.AuthMode.OPEN
    'auth_modes': [wifi.AuthMode.WPA2, wifi.AuthMode.PSK], # [wifi.AuthMode.OPEN]
    'hostname': 'datalogger'                               # msdn hostname
  }

# --- turn on LED on sensor-pcb   --------------------------------------------

if hasattr(pins,"PIN_SWD"):
  switch_d = DigitalInOut(pins.PIN_SWD)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True
elif hasattr(pins,'PIN_LED'):
  switch_d = DigitalInOut(pins.PIN_LED)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True

# --- set CS of display to high   --------------------------------------------

if g_config.HAVE_DISPLAY and hasattr(pins,"PIN_DISP_CS"):
  cs_display = hw_helper.get_dio(pins.PIN_DISP_CS,"DISP_CS")
  cs_display.switch_to_output(value=True)

# --- read rtc   -------------------------------------------------------------

i2c  = hw_helper.init_i2c(pins,g_config)
rtc  = hw_helper.init_rtc(pins,g_config,i2c)
ap_config["rtc"] = rtc  # pass to webap for later use

# --- mount sd-card if available   -------------------------------------------

if g_config.HAVE_SD and hw_helper.init_sd(pins,g_config):
    ap_config["csv_root"] = "/sd"
else:
  try:
    import os
    os.listdir("/saves")
    ap_config["csv_root"] = "/saves"
  except:
    ap_config["csv_root"] = None

# --- put info on display if available   -------------------------------------

if g_config.HAVE_DISPLAY:
  import displayio
  from adafruit_bitmap_font import bitmap_font
  from adafruit_display_text import label as label
  from vectorio import Rectangle
  from display import Display

  g_logger.print("starting display update")
  if hasattr(pins,"PIN_DISP_CS"):
    cs_display.deinit()
  display = Display(g_config).get_display()

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

  # cleanup (free memory)
  g_logger.print(f"free memory before cleanup: {gc.mem_free()}")
  for _ in range(len(group)):
    group.pop()
  group   = None
  font    = None
  shader  = None
  heading = None
  ap_info = None
  ap_info_text = None
  display.root_group = None
  gc.collect()
  g_logger.print(f"free memory after  cleanup: {gc.mem_free()}")

# --- start AP and web-server   ----------------------------------------------

g_logger.print("!!! Starting in ADMIN-Mode !!!")
server = webap.WebAP(config=ap_config)
server.run()
