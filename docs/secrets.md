WLAN credentials
================

The datalogger only connects to a WLAN to initially set the RTC or to
send data using UDP. The former needs the configuration `NET_UPDATE =
True`. UDP data transfer is used when you add the task `send_udp` to
the list of configured tasks.

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
    
    secrets.time_url = 'http://worldtimeapi.org/api/ip'

    # UDP-target configuration (task send_udp)
    secrets.udp_ip   = '1.2.3.4'
    secrets.udp_port = 6600

You can find a template file for `secrets.py` in `src/sec_template.py`.
