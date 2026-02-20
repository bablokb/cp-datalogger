# ----------------------------------------------------------------------------
# wifi_impl_builtin.py: Wifi-implementation for builtin wifi
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pcp-pico-datalogger
#
# ----------------------------------------------------------------------------

import board
import time
import ssl
import adafruit_requests

from log_writer import Logger
from secrets import secrets
from singleton import singleton

class _Radio:
  """ fake Radio implementation """
  def __init__(self):
    self._enabled = True
  @property
  def enabled(self):
    return self._enabled
  @enabled.setter
  def enabled(self,value):
    """ ignore value """
    pass

@singleton
class WifiImpl:
  """ Wifi-implementation for MCU with integrated wifi """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self.logger = Logger()                 # reuse global settings

    try:
      import socketpool
      self._radio = None
    except:
      try:
        import adafruit_wiznet5k.adafruit_wiznet5k_socketpool as socketpool
        self._radio = _Radio()
        self._eth = None
      except:
        self.logger.print("neither socketpool nor wiznet5k_socketpool available")
        raise
    self._socketpool = socketpool

    if not hasattr(secrets,'channel'):
      secrets.channel = 0
    if not hasattr(secrets,'timeout'):
      secrets.timeout = None

    self._pool     = None
    self._requests = None
    self._socket   = None

  # --- connect to AP and to remote-port   -----------------------------------

  def _connect_wlan():
    """ connect to wlan using builtin radio """

    if not self._radio:
      import wifi
      self._radio = wifi.radio

    if not self._radio.enabled:
      self._radio.enabled = True
      self._pool = None
      self._requests = None

    if self._radio.connected and self._pool:
      return
    else:
      self._pool = None
      self._requests = None

    self.logger.print("connecting to %s" % secrets.ssid)
    retries = secrets.retry
    while True:
      try:
        self._radio.connect(secrets.ssid,
                           secrets.password,
                           channel = secrets.channel,
                           timeout = secrets.timeout
                           )
        break
      except:
        self.logger.print("could not connect to %s" % secrets.ssid)
        retries -= 1
        if retries == 0:
          raise
        time.sleep(1)
        continue
    self.logger.print("connected to %s" % secrets.ssid)

  # --- connect to ethernet   ------------------------------------------------

  def _connect_eth(self):
    """ initialize connection """

    if self._eth:
      return

    import pins
    import hw_helper
    self._eth = hw_helper.init_w5k(pins,self.logger)
    self._pool = None
    self._requests = None

  # --- connect and initialize   ---------------------------------------------

  def connect(self):
    """ initialize connection """

    if hasattr(self,"_eth"):  # using a wiznet-chip
      self._connect_eth()
    else:
      self._connect_wlan()

    if not self._pool:
      phy = getattr(self,"_eth",self._radio)
      self._pool = self._socketpool.SocketPool(phy)
      self._requests = None

  # --- return requests-object   --------------------------------------------

  def _get_request(self):
    """ return requests-object """
    if not self._requests:
      self._requests = adafruit_requests.Session(self._pool,
                                                 ssl.create_default_context())
    return self._requests

  # --- return implementing radio   -----------------------------------------

  @property
  def radio(self):
    """ return radio """
    return self._radio

  # --- execute get-request   -----------------------------------------------

  def get(self,url,**kwargs):
    """ process get-request """
    self.connect()
    self.logger.print(f"wifi: get({url})")
    return self._get_request().get(url,**kwargs)

  # --- execute sendto-command   --------------------------------------------

  def sendto(self,data,udp_ip,udp_port):
    """ send to given destination """
    self.connect()
    self.logger.print(f"wifi: send to {udp_ip}:{udp_port}")
    with self._pool.socket(family=socketpool.SocketPool.AF_INET,
                           type=socketpool.SocketPool.SOCK_DGRAM) as socket:
      socket.sendto(data,(udp_ip,udp_port))

  # --- execute send-command   ----------------------------------------------

  def send(self, data, tcp_ip, tcp_port, socket=None):
    """ send to given destination """
    if not len(data):
      self.logger.print(f"wifi: ignoring send request with length 0")
      return
    self.connect()
    self.logger.print(f"wifi: send to {tcp_ip}:{tcp_port}")
    if socket:
      # try to use the socket, but it might already be closed
      try:
        n = socket.send(data)
      except:
        n = -1
      if n <= 0:
        socket = None
      else:
        return (socket,n)

    # (re-) create socket
    socket = self._pool.socket(family=socketpool.SocketPool.AF_INET,
                                 type=socketpool.SocketPool.SOCK_STREAM)
    socket.connect((tcp_ip,tcp_port))
    # return socket for later use
    return (socket, socket.send(data))

  # --- no specific deep-sleep mode   ---------------------------------------

  def deep_sleep(self):
    """ disable radio """

    try:                                       # wifi might not be imported
      self._radio.enabled = False
    except:
      pass
