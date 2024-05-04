#-----------------------------------------------------------------------------
# Wrapper class for OLED-display (currently used in broadcast-mode)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import displayio
from adafruit_displayio_ssd1306 import SSD1306

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
    oled = SSD1306(display_bus,width=int(width),height=int(height))
