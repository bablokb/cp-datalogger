#-----------------------------------------------------------------------------
# Configuration of the AP. Can be left as is unless you are paranoid.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from wifi import AuthMode
ap_config = {
  'debug': False,
  'cache': True,
  'ssid': 'gateway',
  'password': '12345678',                      # ignored for wifi.AuthMode.OPEN
  'auth_modes': [AuthMode.WPA2, AuthMode.PSK], # [wifi.AuthMode.OPEN]
  'hostname': 'gateway'                        # msdn hostname
}
