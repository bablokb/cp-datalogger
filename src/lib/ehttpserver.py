import gc
import time
import re
import errno
import os

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/bablokb/ehttpserver.git"

class BufferedNonBlockingSocket:
  def __init__(self, sock, now, buffer_size=1024):
    self.sock = sock
    self.read_buffer = bytearray(buffer_size)
    self.start, self.end = 0, 0
    self.last_io_time = now

  def read(self, size=-1, stop_byte=None):
    self.last_io_time = time.monotonic()
    while True:
      # fulfill as much of the request as possible from the buffer
      if stop_byte is not None:
        try:
          new_size = self.read_buffer[self.start:].index(stop_byte) + 1  # stop immediately after encountering the stop byte
          size = min(size, new_size) if size >= 0 else new_size
        except ValueError:
          pass
      buffer_slice = self.read_buffer[self.start:min(self.end, self.start + size) if size >= 0 else self.end]
      if buffer_slice:
        yield buffer_slice
      size -= len(buffer_slice)
      self.start += len(buffer_slice)
      if size == 0:  # request satisfied
        break

      # request still unsatisfied, refresh buffer and try again
      self.start, self.end = 0, 0
      try:
        self.end = self.sock.recv_into(self.read_buffer, len(self.read_buffer))
        if self.end == 0:  # client closed connection, there's no more to read
          break
      except OSError as e:
        if e.errno != errno.EAGAIN:
          raise
      yield b""  # client is not done sending yet, try again

  def write(self, data):
    self.last_io_time = time.monotonic()
    bytes_sent = 0
    while bytes_sent < len(data):
      yield
      try:
        bytes_sent += self.sock.send(data[bytes_sent:])
      except OSError as e:
        if e.errno != errno.EAGAIN:  # still pending, try again
          raise


class Response:
  def __init__(self, body, status_code=200, content_type="text/plain", headers={}):
    self.headers = headers
    self.headers["content-type"] = content_type
    if not body is None:
      self.body_bytes = body if isinstance(body, bytes) else body.encode("ascii")
      self.headers["content-length"] = len(self.body_bytes)
    self.status_code = status_code

  def serialize(self):
    response = bytearray(
      f"HTTP/1.1 {self.status_code} {self.status_code}\r\n".encode("ascii"))
    for name, value in self.headers.items():
      response += f"{name}: {value}\r\n".encode("ascii")
    yield response + b"\r\n" + self.body_bytes

class FileResponse(Response):
  """
  Minimal support for serving static files. Silently assume gzip is supported.

  Use it from a handler, e.g.
  ```
    @route("/config.html","GET")
    def handle_get_config(self,path,query_params, headers, body):
      return ehttpserver.FileResponse("/www/config.html")
  ```
  """

  CONTENT_TYPE_MAP = {
    'html': 'text/html',
    'js': 'text/javascript',
    'css': 'text/css',
    'png': 'image/png',
    'json': 'application/json'
    }
  def __init__(self, filename, headers={}, content_type=None):
    try:
      suffix = filename.split('.')[-1]
      try:
        # search for gzipped version first
        file_length = os.stat(filename+".gz")[6]
        self._filename = filename+".gz"
        headers["content-encoding"] = "gzip"
        headers["content-length"] = file_length
      except:
        # no compressed version found, use given filename
        try:
          file_length = os.stat(filename)[6]
          self._filename = filename
          headers["content-length"] = file_length
          if "content-encoding" in headers.keys():
            del headers["content-encoding"]
        except:
          # not found at all
          raise

      if not content_type:
        if suffix in self.CONTENT_TYPE_MAP:
          content_type = self.CONTENT_TYPE_MAP[suffix]
        else:
          content_type = "text/plain"
      super().__init__(None,status_code=200,content_type=content_type,
                       headers=headers)
    except:
      super().__init__("",status_code=400,headers=headers)
      self._filename = None

  def serialize(self):
    if not self._filename:
      yield from super().serialize()
      return
    response = bytearray(
      f"HTTP/1.1 {self.status_code} {self.status_code}\r\n".encode("ascii"))
    for name, value in self.headers.items():
      response += f"{name}: {value}\r\n".encode("ascii")
    yield response + b"\r\n"

    with open(self._filename,"rb") as file:
      while True:
        buf = file.read(1024)
        if buf:
          yield buf
        else:
          return

def route(path, method='GET'):
  def register_route(request_handler):
    Server.routes.append((f"^{path}$", method, request_handler))
  return register_route

class Server:
  """ This implements the webserver class.
  To use it, create a subclass and implement request handlers
  for routes as methods 
  """

  routes = []

  # --- constructor   --------------------------------------------------------

  def __init__(self, max_request_line_size=4096,
               max_header_count=50,
               max_body_bytes=65536,
               request_timeout_seconds=10,debug=False):
    """ constructor """
    self._max_request_line_size = max_request_line_size
    self._max_header_count = max_header_count
    self._max_body_bytes = max_body_bytes
    self._request_timeout_seconds = request_timeout_seconds
    self._debug = debug

  # --- start server   -------------------------------------------------------

  def start(self, server_socket,
            listen_on=('0.0.0.0', 80), max_parallel_connections=5):
    """ start server """
    server_socket.setblocking(False)
    server_socket.bind(listen_on)
    server_socket.listen(max_parallel_connections)
    client_processors = []
    while True:
      if len(client_processors) < max_parallel_connections:
        try:
          new_client_socket, new_client_address = server_socket.accept()
        except OSError as e:
          if e.errno != errno.EAGAIN:
            raise
          # no connectings pending, try again
        else:
          self.debug(f"accepted connection from {new_client_address}")
          bnb_socket = BufferedNonBlockingSocket(new_client_socket,
                                                 time.monotonic())
          client_processors.append(
            (new_client_socket,
             bnb_socket,
             self.process_client_connection(
               bnb_socket
             )
            )
          )

      # step through open client connections
      now = time.monotonic()
      new_client_processors = []
      for client_socket, bnb_socket,client_processor in client_processors:
        try:
          if now - bnb_socket.last_io_time > self._request_timeout_seconds:
            raise StopIteration()  # timed out
          next(client_processor)
        except Exception as e:
          client_socket.close()
          if not isinstance(e, StopIteration):
            raise
        else:
          new_client_processors.append(
            (client_socket,bnb_socket,client_processor)
          )
      client_processors = new_client_processors
      yield

  # --- print a debug-message   ----------------------------------------------

  def debug(self,msg):
    """ print a debug-message """
    if self._debug:
      print(msg)

  # --- decode html-escape chars   -------------------------------------------

  def html_decode(self,text):
    """ decode html esc-chars (subset only!) """

    token = text.split('%')
    result = token.pop(0)
    for t in token:
      decoded = chr(int(t[:2],16))
      result = f"{result}{decoded}{t[2:]}"
    return result

  # --- handle requests   ----------------------------------------------------

  def _handle_request(self, target, method, headers, content_length,
                      buffered_client_socket):
    """ dispatch requests to defined request-handlers """

    self.debug(f"_handle_request for {target}")
    if content_length > self._max_body_bytes:
      yield from Response("Content Too Large", 413).serialize()
      return

    # read request body
    body = bytearray()
    for data in buffered_client_socket.read(size=content_length):
      yield b""
      body += data

    # extract path and query-parameters
    path, query_parameters = (
      target.split("?", 1) if "?" in target else (target, "")
    )

    # map path to routes
    for route_path, route_method, request_handler in self.routes:
      if method == route_method and re.match(route_path,path):
        response = request_handler(self,path,query_parameters, headers, body)
        self.debug(f"response status: {response.status_code}")
        self.debug(f"sending {response.headers['content-length']} bytes")
        yield from response.serialize()
        gc.collect()
        return
    yield from Response("Not Found", 404).serialize()
    return

  # --- process client-connection   ------------------------------------------

  def process_client_connection(self, buffered_client_socket):
    try:
      # read start line
      start_line = bytearray()
      for data in buffered_client_socket.read(size=self._max_request_line_size,
                                              stop_byte=b'\n'):
        yield
        start_line += data
      self.debug(f"received request {start_line}")

      # parse start line
      if start_line[-1:] != b'\n':
        self.debug("excessively long or invalid start line, giving up")
      try:
        method, target, _ = start_line.decode("ascii").split(" ", 2)
      except (UnicodeError, ValueError):
        self.debug("malformed start line, giving up")
        return

      # parse headers and request body
      headers = {}
      for _ in range(self._max_header_count + 1):
        header_line = bytearray()
        for data in buffered_client_socket.read(size=self._max_request_line_size,
                                                stop_byte=b'\n'):
          yield
          header_line += data

        if header_line[-1:] != b"\n":
          self.debug("excessively long or invalid header, giving up")
          return

        if header_line == b"\r\n":  # end of headers
          break

        try:
          header_line = header_line.decode("ascii")
        except UnicodeError:
          self.debug("malformed header, giving up")
          return

        if ":" not in header_line:
          self.debug("malformed header, giving up")
          return

        header_name, header_value = header_line.split(":", 1)
        headers[header_name.strip().lower()] = header_value.strip()
        yield
      else:
        self.debug("too many headers, giving up")
        return

      # generate and send response
      try:
        content_length = max(0, int(headers.get('content-length', '0')))
      except ValueError:
        self.debug("malformed content-length header, giving up")
        return

      for data in self._handle_request(target, method, headers,
                                       content_length, buffered_client_socket):
        yield
        for _ in buffered_client_socket.write(data):
          yield

    except OSError as e:  # errno.EPIPE=32 not available in CP
      if e.errno not in (errno.ECONNRESET, errno.ENOTCONN, 32):
        raise
