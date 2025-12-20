#-----------------------------------------------------------------------------
# Optimized sleep:
#
#   - use light-sleep/deep-sleep
#   - support duration and time-point
#
# Notes:
#
#   - the alarm-module is currently not implemented for RP2350
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

MIN_SLEEP_DURATION = 5

import time

try:
  import alarm
  HAVE_ALARM = True
except:
  HAVE_ALARM = False
import microcontroller

# --- class Sleep   ----------------------------------------------------------

class TimeSleep:
  """ minimal wrapper class for light and deep sleep """

  @classmethod
  def _get_alarm_since_epoch(cls,until=None):
    """ convert until to seconds since epoch """

    if until is None:
      return None
    if isinstance(until,int):
      return until
    return time.mktime(until)

  @classmethod
  def _sleep_impl(cls,duration=0,until=None,sleep_func=None):
    """ implement sleep """

    if until:
      try:
        time_alarm = alarm.time.TimeAlarm(epoch_time=until)
      except:
        # "until" might be in the past for short-term sleeps
        return
    elif duration >= MIN_SLEEP_DURATION:
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+duration)
    else:
      time.sleep(duration)
      return

    sleep_func(time_alarm)   # the code below won't execute with deep-sleep!

  # --- light sleep   ----------------------------------------------------------

  @classmethod
  def light_sleep(cls,duration=0,until=None):

    """ sleep the given duration or until given time-point """
    ep_alarm = TimeSleep._get_alarm_since_epoch(until)
    if not HAVE_ALARM:
      # fallback to time.sleep
      if ep_alarm:
        time.sleep(ep_alarm-time.time())
      else:
        time.sleep(duration)
      return

    TimeSleep._sleep_impl(duration=duration,until=ep_alarm,
                      sleep_func=alarm.light_sleep_until_alarms)

  # --- deep sleep   ----------------------------------------------------------

  @classmethod
  def deep_sleep(cls,duration=0,until=None):

    """ sleep the given duration or until given time-point """
    ep_alarm = TimeSleep._get_alarm_since_epoch(until)
    if not HAVE_ALARM:
      # fallback to time.sleep
      if ep_alarm:
        time.sleep(ep_alarm-time.time())
      else:
        time.sleep(duration)
      return

    TimeSleep._sleep_impl(duration=duration,until=ep_alarm,
                      sleep_func=alarm.exit_and_deep_sleep_until_alarms)
