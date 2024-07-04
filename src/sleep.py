#-----------------------------------------------------------------------------
# Optimized sleep:
#
#   - use light-sleep
#   - reduce cpu-frequency
#   - support duration and time-point
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

CPU_FREQ_LOW =  40000000

import time
import alarm

# --- light sleep   ----------------------------------------------------------

def light_sleep(duration=0,until=None):
  """ sleep the given duration or until given time-point """

  if until:
    wakeup_alarm = alarm.time.TimeAlarm(
      epoch_time=time.mktime(until))
  elif duration >= 2:
    time_alarm = alarm.time.TimeAlarm(
      monotonic_time=time.monotonic()+duration)
  else:
    time.sleep(duration)
    return

  try:
    old_freq = microcontroller.cpu.frequency
    microcontroller.cpu.frequency = CPU_FREQ_LOW
    have_freq = True
  except:
    have_freq = False
  alarm.light_sleep_until_alarms(time_alarm)
  if have_freq:
    try:
      microcontroller.cpu.frequency = old_freq
    except:
      pass

# --- enter deep-sleep   -----------------------------------------------------

def deep_sleep(until=None):
  """ enter deep-sleep """
  if not until:
    return
  wakeup_alarm = alarm.time.TimeAlarm(epoch_time=time.mktime(until))
  alarm.exit_and_deep_sleep_until_alarms(wakeup_alarm)
