#-----------------------------------------------------------------------------
# Pico initialization file after hard reset. This file will check if
# certain GPs are low (e.g. button SW-A is pressed) and will enter
# special modes (e.g. admin-mode, broadcast-mode).
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
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
  'BTN_C_CODEFILE': 'bootloader.py',
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

if a_pressed() and btn_opts['BTN_A_CODEFILE'] and not b_pressed():
  if btn_opts['BTN_A_FLASH_RW']:       # make flash writable
    storage.remount("/",False)
  supervisor.set_next_code_file(btn_opts['BTN_A_CODEFILE'],sticky_on_reload=True)
  supervisor.reload()

# --- check if switch B is pressed and if so, enter broadcast-mode   ---------

if b_pressed() and btn_opts['BTN_B_CODEFILE'] and not a_pressed():
  if btn_opts['BTN_B_FLASH_RW']:       # make flash writable
    storage.remount("/",False)
  supervisor.set_next_code_file(btn_opts['BTN_B_CODEFILE'],sticky_on_reload=True)
  supervisor.reload()

# --- check if switch C is pressed and if so, enter firmware-mode   ---------

if c_pressed() and btn_opts['BTN_C_CODEFILE']:
  if btn_opts['BTN_C_FLASH_RW']:       # make flash writable
    storage.remount("/",False)
  supervisor.set_next_code_file(btn_opts['BTN_C_CODEFILE'],sticky_on_reload=True)
  supervisor.reload()

# --- check if A+B is pressed and reset RTC   --------------------------------
# Resetting the RTC only makes sense if NET_UPDATE is True. The reset
# will trigger an update at next boot. Use case: start/end of DST

if a_pressed() and b_pressed():
  import time
  try:
    from log_config import g_logger
  except:
    from log_writer import Logger
    g_logger = Logger(None)
  import hw_helper
  from settings import Settings
  g_config = Settings(g_logger)
  g_config.import_config()

  i2c  = hw_helper.init_i2c(g_config)
  rtc  = hw_helper.init_rtc(g_config,i2c)
  rtc.update(time.struct_time((2022,1,1,12,00,00,5,1,-1)))
