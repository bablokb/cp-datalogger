#-----------------------------------------------------------------------------
# Configuration of the AP.
#
# !!! This file is not maintained within Github !!!
#
# Author: Bernhard Bablok
#
# Website: https://github.com/cp-datalogger
#-----------------------------------------------------------------------------

from wifi import AuthMode
ap_config = {
  'debug': False,
  'cache': True,
  'ssid': 'datalogger',
  'password': '12345678',                      # ignored for wifi.AuthMode.OPEN
  'auth_modes': [AuthMode.WPA2, AuthMode.PSK], # [wifi.AuthMode.OPEN]
  'hostname': 'datalogger'                     # msdn hostname
}
