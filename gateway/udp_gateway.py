#-----------------------------------------------------------------------------
# Sample UDP code for a gateway.
#
# Adapted from: https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import socket

# --- process data   ---------------------------------------------------------

def process_data(data):
  """ process data (e.g. send into the cloud) """
  print(f"data: {data}",end='')

# --- main-loop   ------------------------------------------------------------

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 6600))

while True:
  data, address = server_socket.recvfrom(80)
  process_data(data.decode(encoding="UTF-8"))
