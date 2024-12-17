#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Simple UDP/TCP receiver.
# This program should run as a central server, either serving dataloggers
# directly, or via a relaying gateway using an UDP/TCP-sender component.
#
# Code taken and adapted from:
# https://stackoverflow.com/questions/5160980/use-select-to-listen-on-both-tcp-and-udp-message
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import sys
import argparse
from socket import *
from select import select

class SocketReceiver:
  def __init__(self,port=8888,backlog=5,filename="/dev/stdout"):
    """ constructor """
    self._filename = filename
    self._data = bytearray(1024)

    # create tcp socket
    self._tcp_socket = socket(AF_INET, SOCK_STREAM)
    self._tcp_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    self._tcp_socket.bind(('',port))
    self._tcp_socket.listen(backlog)

    # create udp socket
    self._udp_socket = socket(AF_INET, SOCK_DGRAM)
    #self._udp_socket.settimeout(0.5)
    self._udp_socket.bind(('',port))

    self._input = [self._tcp_socket,self._udp_socket]

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    try:
      self._tcp_socket.shutdown(SHUT_RDWR)
      self._tcp_socket.close()
      self._udp_socket.close()
    except:
      raise

  # --- print error messages to stderr   -------------------------------------

  def print_err(self,*args):
    """ print to stderr """
    print(*args,file=sys.stderr,flush=True)

  # --- save data to output file   -------------------------------------------

  def save_data(self,values):
    """ save data to file """
    if not values[-1] == '\n':
      values.append('\n')
    with open(self._filename, "a") as file:
      file.write(f"{values}")

  # --- handle connect event   -----------------------------------------------

  def connect_tcp(self,sock):
    """ handle connect for server-socket """
    csock, addr = sock.accept()
    self.print_err(f"connect_tcp: connect {csock} from {addr}")
    return csock

  # --- read from TCP-socket   -----------------------------------------------

  def read_tcp(self,sock):
    """ read from TCP-socket """
    self.print_err(f"read_tcp: reading from {sock}")
    n = sock.recv_into(self._data)
    self.save_data(self._data[:n].decode())
    self.print_err(
      f"read_tcp: {n} bytes from {sock.getpeername()}: {self._data[:n].decode()}")
    sock.close()

  # --- read from TCP-socket   -----------------------------------------------

  def read_udp(self,sock):
    """ read from UDP-socket """
    self.print_err(f"read_udp: reading from {sock}")
    n,*addr = sock.recvfrom_into(self._data)
    self.save_data(self._data[:n].decode())
    self.print_err(f"read_udp: {n} bytes from {addr}: {self._data[:n].decode()}")

  # --- main processing loop   -----------------------------------------------

  def run(self):
    """ main processing loop """

    while True:
      inputready,outputready,exceptready = select(self._input,[],[])
  
      for sock in inputready:
        if sock == self._tcp_socket:
          csock = self.connect_tcp(sock)
          self._input.append(csock)
        elif sock == self._udp_socket:
          self.read_udp(sock)
        else:
          self.read_tcp(sock)
          self._input.remove(sock)

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="UDP Receiver")
  parser.add_argument("--port", type=int, default=5005,
                      help="UDP/TCP receiver port (default: 5005)")
  parser.add_argument("--backlog", type=int, default=5,
                      help="TCP listen-backlog (default: 5)")
  parser.add_argument("--outfile", type=str, default="/dev/stdout",
                      help="Filename")
  args = parser.parse_args()    
  try:
    receiver = SocketReceiver(port=args.port,
                              backlog=args.backlog,
                              filename=args.outfile)
    receiver.run()
  except BaseException as ex:
    receiver.print_err(f"exception: {ex}")
    receiver.cleanup()
    if not isinstance(ex,KeyboardInterrupt):
      raise
