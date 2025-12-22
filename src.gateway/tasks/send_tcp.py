#-----------------------------------------------------------------------------
# Gateway-task: send (buffered data) to destination using TCP.
#
# Add to S_TASKS to execute this task as a shutdown task. The task will then
# send all buffered data (from /sd/tx_buffer.csv) at once.
#
# You *can* use it as a normal data-task as well, in this case only the values
# passed as argument are transmitted. Note that single data-transfers are
# not efficient.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

CHUNK = 1024
import os
import time

from log_writer import Logger
g_logger = Logger()

from wifi_impl_builtin import WifiImpl

def run(config, app, msg_type, values):
  """ send buffered data to TCP-destination """

  # if values only has one item (a timestamp), it needs the buffered data
  # on the SD-card. If it is not present, bail out.
  if len(values) == 1 and not hasattr(config,"HAVE_SD"):
    return

  if len(values) == 1:
    csv_file = "/sd/tx_buffer.csv"
    try:
      status = os.stat(csv_file)
      size = status[6]
      if size == 0:
        g_logger.print(f"send_tcp: empty file /sd/tx_buffer.csv")
        os.remove(csv_file)
        return
    except:
      # file does not exist
      g_logger.print(f"send_tcp: no data file /sd/tx_buffer.csv")
      return

  wifi = WifiImpl()
  host = config.TCP_HOST
  port = config.TCP_PORT

  if len(values) == 1:
    # fetch all data and send it.
    g_logger.print(f"send_tcp: sending buffered data to {host}:{port}...")
    sent = 0
    socket = None
    with open(csv_file,"rb") as file:
      data = file.read(CHUNK)
      socket, n = wifi.send(data,host,port)
      sent += n
      if sent == size:
        socket.close()
        os.remove(csv_file)
        return
  else:
    g_logger.print(f"send_tcp: sending data to {host}:{port}...")
    # convert values to bytes and send them
    socket, n = wifi.send(bytes(','.join(values)+'\n',"UTF-8"),host,port)
    # ignore n, since we can't do anything about an error anyway
    socket.close()
