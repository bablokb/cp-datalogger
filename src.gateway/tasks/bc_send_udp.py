#-----------------------------------------------------------------------------
# Gateway-task: send broadcast-info to UDP-destination
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time

from log_writer import Logger
g_logger = Logger()

from wifi_impl_builtin import WifiImpl

def run(config, app, msg_type, values):
  """ send broadcast-info to UDP-destination """

  if msg_type != "B":
    g_logger.print(f"gateway: bc_save_data: illegal msg_type: {msg_type}")
    return

  wifi = WifiImpl()
  host = config.BC_UDP_HOST
  port = config.BC_UDP_PORT
  g_logger.print(f"gateway: sending broadcast data to {host}:{port}...")
  wifi.sendto(bytes(','.join(values)+'\n',"UTF-8"),host,port)
