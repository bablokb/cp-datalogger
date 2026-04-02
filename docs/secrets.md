WLAN credentials
================

The datalogger only connects to a WLAN to initially set the RTC or to
send data using UDP/TCP. The former needs the configuration `NET_UPDATE =
True`. UDP/TCP data transfer is used when you add the tasks `send_udp`
or `send_tcp` to the list of configured tasks.

The configuration file must create a `Settings`-object with a set of
defined attributes:

    class Settings:
      pass
    
    secrets = Settings()
    
    secrets.ssid      = 'my_wlan_ssid'
    secrets.password  = 'my_very_secret_password'
    secrets.retry     = 2
    secrets.debugflag = False
    #secrets.channel   = 6         # optional
    #secrets.timeout   = 10        # optional

    # this URL is no longer functional
    secrets.time_url = 'http://worldtimeapi.org/api/ip'

You can find a template file for `secrets.py` in `src/sec_template.py`.
