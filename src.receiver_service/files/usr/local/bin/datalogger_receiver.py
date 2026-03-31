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
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import sys
import argparse
from socket import *
from select import select

from datalogger_shared import Tools

class SocketReceiver:
  def __init__(self,args):
    """ constructor """

    self._tools = Tools(debug=args.debug)
    self.debug = self._tools.debug
    # receiver settings
    port = args.port if args.port else (
      int(self._tools.get_value(
        "RECEIVER",
        "port",8888)))
    backlog = int(self._tools.get_value(
      "RECEIVER",
      "backlog",5))
    bufsize = int(self._tools.get_value(
      "RECEIVER",
      "bufsize",1024))
    self._tools.debug(f"receiver settings: {port=}, {backlog=}, {bufsize=}")
    self._data = bytearray(bufsize)

    # tasks settings
    tasks =  args.tasks if args.tasks else (
      self._tools.get_value(
        "RECEIVER",
        "tasks","noop"))
    self._tasks = []
    for task in tasks.split(" "):
      try:
        self._tools.debug(f"{task}: loading")
        task_module = __import__("tasks."+task,
                                 globals(),locals(),[task.upper()],level=0)
        task_class = getattr(task_module,task.upper())
        self._tasks.append((task,task_class()))
      except Exception as ex:
        self._tools.debug(f"{task}: loading failed: exception: {ex}")

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

  # --- read configuration value   --------------------------------------------

  def _get_value(self,parser,section,option,default):
    """ get value of config-variables and return given default if unset """

    if parser.has_section(section):
      try:
        value = parser.get(section,option)
      except:
        value = default
    else:
      value = default
    return value

  # --- run configured tasks   -----------------------------------------------

  def _run_tasks(self, init=False, record=None):
    """ run tasks """

    for task_name,task in self._tasks:
      try:
        self._tools.debug(f"{task_name}: starting")
        task.run(record)
        self._tools.debug(f"{task_name}: ended")
      except Exception as ex:
        self._tools.debug(f"{task_name}: failed: exception: {ex}")
        raise

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    try:
      self._tcp_socket.shutdown(SHUT_RDWR)
      self._tcp_socket.close()
      self._udp_socket.close()
    except:
      raise

  # --- handle connect event   -----------------------------------------------

  def connect_tcp(self,sock):
    """ handle connect for server-socket """
    csock, addr = sock.accept()
    self._tools.debug(f"connect_tcp: connect {csock} from {addr}")
    return csock

  # --- read from TCP-socket   -----------------------------------------------

  def read_tcp(self,sock):
    """ read from TCP-socket """
    self._tools.debug(f"read_tcp: reading from {sock}")
    try:
      n = sock.recv_into(self._data)
      self._tools.debug(
        f"read_tcp: {n} bytes from {sock.getpeername()}: {self._data[:n].decode()}")
      if n == 0:
        self._tools.debug(f"read_tcp: socket closed")
        return True
      elif n < 0:
        self._tools.debug(f"read_tcp: socket failure")
        return True
    except:
      self._tools.debug(
        f"read_tcp: failed to read from {sock.getpeername()}")
      return True
    self._run_tasks(record=self._data[:n])
    return False

  # --- read from TCP-socket   -----------------------------------------------

  def read_udp(self,sock):
    """ read from UDP-socket """
    self._tools.debug(f"read_udp: reading from {sock}")
    n,*addr = sock.recvfrom_into(self._data)
    self._run_tasks(record=self._data[:n].decode())
    self._tools.debug(f"read_udp: {n} bytes from {addr}: {self._data[:n].decode()}")

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
          if self.read_tcp(sock):
            self._input.remove(sock)

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="UDP/TCP Receiver")
  parser.add_argument("-p", "--port", type=int, default=None,
                      help="UDP/TCP receiver port (default: 8888)")
  parser.add_argument("-t", "--tasks", type=str, default=None,
                      help="tasks for received data")
  parser.add_argument('-d', '--debug', action='store_true',
                      dest='debug', default=None,
                      help="debug-mode (writes to stderr)")

  args = parser.parse_args()    
  receiver = SocketReceiver(args)
  try:
    receiver.run()
  except BaseException as ex:
    receiver.debug(f"exception: {ex}")
    receiver.cleanup()
    if not isinstance(ex,KeyboardInterrupt):
      raise
