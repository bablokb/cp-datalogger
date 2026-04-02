#-----------------------------------------------------------------------------
# Task: send data using UDP
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

from wifi_impl_builtin import WifiImpl

def run(config,app):
  """ send data using UDP """
  wifi = WifiImpl()
  g_logger.print(f"UDP: sending data to {config.UDP_IP}:{config.UDP_PORT}")
  wifi.sendto(bytes(app.record+'\n',"UTF-8"),config.UDP_IP,config.UDP_PORT)
