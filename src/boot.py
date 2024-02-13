#-----------------------------------------------------------------------------
# Pico initialization file after hard reset. This file will check if
# GP12 is low (i.e. button SW-A is pressed) and enter admin-mode by
# restarting into admin.py.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import board
import storage
import supervisor
from digitalio import DigitalInOut, Pull, Direction

import pins
from config import TEST_MODE

# --- configure hardware   ---------------------------------------------------

switch_a = DigitalInOut(pins.PIN_SWA)
switch_a.direction = Direction.INPUT
switch_a.pull = Pull.UP

switch_b = DigitalInOut(pins.PIN_SWB)
switch_b.direction = Direction.INPUT
switch_b.pull = Pull.UP

switch_c = DigitalInOut(pins.PIN_SWC)
switch_c.direction = Direction.INPUT
switch_c.pull = Pull.UP

led_d = DigitalInOut(pins.PIN_SWD)
led_d.direction = Direction.OUTPUT

# --- blink LED on button-press   --------------------------------------------

if TEST_MODE or not switch_a.value or not switch_b.value or not switch_c.value:
  for _ in range(3):
    led_d.value = True
    time.sleep(0.15)
    led_d.value = False
    time.sleep(0.15)

# --- check if switch A is pressed and if so, enter admin-mode   -------------

if not switch_a.value:
  # make flash writable
  storage.remount("/",False)
  supervisor.set_next_code_file("admin.py",sticky_on_reload=True)
  supervisor.reload()
