# ----------------------------------------------------------------------------
# WLAN credentials. Note that for datalogger operation, credentials are
# only required if you use WLAN, i.e. you either
#   - set NET_UPDATE=True and configure a time-server or
#   - use one of the WLAN based tasks
#
# Normally, you can just leave this file as is.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pcb-pico-datalogger
# ----------------------------------------------------------------------------

class Settings:
  pass

secrets = Settings()

secrets.ssid      = 'my_wlan_ssid'
secrets.password  = 'my_very_secret_password'
secrets.retry     = 2
secrets.debugflag = False
#secrets.channel   = 6         # optional
#secrets.timeout   = 10        # optional

# http://worldtimeapi.org/api/ip is down, others require an API-key
secrets.time_url = None
