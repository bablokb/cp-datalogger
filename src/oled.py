#-----------------------------------------------------------------------------
# Wrapper class for OLED-display (currently used in broadcast-mode)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import busio
import displayio
from adafruit_displayio_ssd1306 import SSD1306
from terminalio import FONT
from adafruit_display_text import label

import pins

class OLED:
  """ Wrapper for SSD1306 I2C-OLED-display """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config,i2c1,i2c0):
    """ constructor """

    width,height,address = config.HAVE_OLED.split(',')
    if not i2c1:
      i2c1 = busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)
    try:
      display_bus = displayio.I2CDisplay(i2c1,device_address=int(address,16))
    except:
      # try ic20
      if not i2c0:
        i2c0 = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
      display_bus = displayio.I2CDisplay(i2c0,device_address=int(address,16))
    self._display = SSD1306(display_bus,width=int(width),height=int(height))

    group = displayio.Group()
    self._textlabel = label.Label(FONT,
                                  text="",
                                  color=0xFFFFFF,line_spacing=1.05,
                                  anchor_point=(0,0),x=0,y=4
                                  )
    group.append(self._textlabel)
    self._display.root_group = group

  # --- return display   -----------------------------------------------------

  def get_display(self):
    """ return display-object """
    return self._display

  # --- return text   ---------------------------------------------------------

  def get_textlabel(self):
    """ return label-object """
    return self._textlabel
