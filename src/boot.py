#-----------------------------------------------------------------------------
# Pico initialization file after hard reset. This file will check if
# certain GPs are low (e.g. button SW-A is pressed) and will enter
# special modes (e.g. admin-mode, broadcast-mode).
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
try:
  import config
  TEST_MODE = config.TEST_MODE
except:
  TEST_MODE = False

# set defaults
btn_opts = {
  'BTN_A_CODEFILE': 'admin.py',
  'BTN_A_FLASH_RW': True,
  'BTN_B_CODEFILE': 'broadcast.py',
  'BTN_B_FLASH_RW': False,
  'BTN_C_CODEFILE': None,
  'BTN_C_FLASH_RW': False
  }

for attrib in btn_opts:
  if hasattr(config,attrib):
    btn_opts[attrib] = getattr(config,attrib)

# --- configure hardware   ---------------------------------------------------

if hasattr(pins,"PIN_SWA"):
  switch_a = DigitalInOut(pins.PIN_SWA)
  switch_a.direction = Direction.INPUT
  switch_a.pull = Pull.UP if pins.PIN_SWA_ACTIVE_LOW else Pull.DOWN
  a_pressed = lambda: (
    not switch_a.value if pins.PIN_SWA_ACTIVE_LOW else switch_a.value)
else:
  a_pressed = lambda: False

if hasattr(pins,"PIN_SWB"):
  switch_b = DigitalInOut(pins.PIN_SWB)
  switch_b.direction = Direction.INPUT
  switch_b.pull = Pull.UP if pins.PIN_SWB_ACTIVE_LOW else Pull.DOWN
  b_pressed = lambda: (
    not switch_b.value if pins.PIN_SWB_ACTIVE_LOW else switch_b.value)
else:
  b_pressed = lambda: False

if hasattr(pins,"PIN_SWC"):
  switch_c = DigitalInOut(pins.PIN_SWC)
  switch_c.direction = Direction.INPUT
  switch_c.pull = Pull.UP if pins.PIN_SWC_ACTIVE_LOW else Pull.DOWN
  c_pressed = lambda: (
    not switch_c.value if pins.PIN_SWC_ACTIVE_LOW else switch_c.value)
else:
  c_pressed = lambda: False

if hasattr(pins,"PIN_SWD"):
  led_d = DigitalInOut(pins.PIN_SWD)
  led_d.direction = Direction.OUTPUT
else:
  led_d = None

# --- blink LED on button-press   --------------------------------------------

if led_d and (TEST_MODE or a_pressed() or b_pressed() or c_pressed()):
  for _ in range(3):
    led_d.value = True
    time.sleep(0.15)
    led_d.value = False
    time.sleep(0.15)

# --- check if switch A is pressed and if so, enter admin-mode   -------------

if a_pressed() and btn_opts['BTN_A_CODEFILE']:
  if btn_opts['BTN_A_FLASH_RW']:       # make flash writable
    storage.remount("/",False)
  supervisor.set_next_code_file(btn_opts['BTN_A_CODEFILE'],sticky_on_reload=True)
  supervisor.reload()

# --- check if switch B is pressed and if so, enter broadcast-mode   ---------

if b_pressed() and btn_opts['BTN_B_CODEFILE']:
  if btn_opts['BTN_B_FLASH_RW']:       # make flash writable
    storage.remount("/",False)
  supervisor.set_next_code_file(btn_opts['BTN_B_CODEFILE'],sticky_on_reload=True)
  supervisor.reload()

# --- check if switch C is pressed and if so, enter broadcast-mode   ---------

if c_pressed() and btn_opts['BTN_C_CODEFILE']:
  if btn_opts['BTN_C_FLASH_RW']:       # make flash writable
    storage.remount("/",False)
  supervisor.set_next_code_file(btn_opts['BTN_C_CODEFILE'],sticky_on_reload=True)
  supervisor.reload()
