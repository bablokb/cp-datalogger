#-----------------------------------------------------------------------------
# Wrapper class for OLED-display (currently used in broadcast-mode)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import atexit
import busio
import displayio
from adafruit_displayio_ssd1306 import SSD1306
from terminalio import FONT
from adafruit_display_text import label

try:
  from i2cdisplaybus import I2CDisplayBus
except:
  I2CDisplayBus = displayio.I2CDisplay

import pins
from singleton import singleton

def at_exit_oled(logger):
  """ release OLED """
  try:
    # may fail if we want to log to SD
    logger.print(f"releasing oled")
  except:
    print(f"releasing oled")
  displayio.release_displays()   # cannot release a specific display

@singleton
class OLED:
  """ Wrapper for SSD1306 I2C-OLED-display """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config,i2c,logger):
    """ constructor """

    displayio.release_displays()
    bus,address,width,height,*rotation = config.HAVE_OLED.split(',')
    if bus != '*':
      display_bus = I2CDisplayBus(i2c[int(bus)],
                                       device_address=int(address,16))
    else:
      display_bus = None
      for bus in i2c:
        if not bus:
          continue
        try:
          display_bus = I2CDisplayBus(bus,device_address=int(address,16))
          break
        except:
          pass
      if not display_bus:
        raise Exception("no OLED found after probing all I2C-busses")

    rotation = int(rotation[0]) if rotation else 0
    self._display = SSD1306(display_bus,width=int(width),
                            height=int(height),
                            rotation=rotation)

    group = displayio.Group()
    self._textlabel = label.Label(FONT,
                                  text="",
                                  color=0xFFFFFF,line_spacing=1.05,
                                  anchor_point=(0,0),x=0,y=4
                                  )
    group.append(self._textlabel)
    self._display.root_group = group
    atexit.register(at_exit_oled,logger)

  # --- return display   -----------------------------------------------------

  def get_display(self):
    """ return display-object """
    return self._display

  # --- return text   ---------------------------------------------------------

  def get_textlabel(self):
    """ return label-object """
    return self._textlabel
