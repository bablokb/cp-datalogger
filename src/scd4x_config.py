#-----------------------------------------------------------------------------
# Start SCD4x autoconfiguration
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
from digitalio import DigitalInOut, Direction
import pins

# --- turn on LED on sensor-pcb   --------------------------------------------

if hasattr(pins,"PIN_SWD"):
  switch_d = DigitalInOut(pins.PIN_SWD)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True
elif hasattr(pins,'PIN_LED'):
  switch_d = DigitalInOut(pins.PIN_LED)
  switch_d.direction = Direction.OUTPUT
  switch_d.value = True


time.sleep(5)
print("starting scd4x_config.autorun()")

from tools import scd4x_config
scd4x_config.autorun()
