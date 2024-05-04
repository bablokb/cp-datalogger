#-----------------------------------------------------------------------------
# Wrapper class for OLED-display (currently used in broadcast-mode)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import displayio
from adafruit_displayio_ssd1306 import SSD1306
from terminalio import FONT
from adafruit_display_text import label

import pins

class OLED:
  """ Wrapper for SSD1306 I2C-OLED-display """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config,i2c1):
    """ constructor """

    width,height,address = config.HAVE_OLED.split(',')
    if not i2c1:
      i2c1 = busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)
    display_bus = displayio.I2CDisplay(i2c1,device_address=int(address,16))
    self._display = SSD1306(display_bus,width=int(width),height=int(height))

    self._lines = ["Starting..."]
    if height == 32:
      self._lines.extend([""]*2)
    else:
      self._lines.extend([""]*5)
    group = displayio.Group()
    self._text = label.Label(FONT,
                             text=self._lines[0],
                             color=0xFFFFFF,line_spacing=1.05,
                             anchor_point=(0,0),x=0,y=4
                             )
    group.append(self._text)
    self._display.show(group)

  # --- return size   --------------------------------------------------------

  def get_size(self):
    """ return display-object """
    return self._display.width,self._display.height

  # --- clear display   ------------------------------------------------------

  def clear(self):
    """ clear display """
    self._lines = [""]*len(self._lines)
    self._text.text = ""

  # --- show text   ----------------------------------------------------------

  def show_text(self,lines,row=0):
    """ show text lines starting at the given row """

    for line in lines:
      if row >= len(self._lines):
        break
      self._lines[row] = line
      row += 1
    self._text.text = "\n".join(self._lines)
