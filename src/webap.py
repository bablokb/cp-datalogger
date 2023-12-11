# -------------------------------------------------------------------------
# Run AP together with a web-server.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import board
import wifi
import biplane
import gc

class WebAP:
  """ Access-point and webserver """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config
    self._server = biplane.Server()
    self._import_config()

    # --- request-handler for /   --------------------------------------------

    @self._server.route("/","GET")
    def _handle_main(query_params, headers, body):
      """ handle request for main-page """
      self.msg("_handle_main...")
      return biplane.Response("<h1>Hello from WebAP!</h1>",
                              content_type="text/html")

    # --- request-handler for /favicon.ico   ---------------------------------

    @self._server.route("/favicon.ico","GET")
    def _handle_favicon(query_params, headers, body):
      """ handle request for favicon """
      self.msg("_handle_favicon...")
      return biplane.Response("",status_code=400)

    # --- request-handler for /utils.js   -------------------------------

    @self._server.route("/utils.js","GET")
    def _handle_utils_js(query_params, headers, body):
      """ handle request for utils.js """
      self.msg(f"_handle_utils_js")
      return biplane.FileResponse("/www/utils.js")

    # --- request-handler for /dl_styles.css   -------------------------------

    @self._server.route("/dl_styles.css","GET")
    def _handle_dl_styles(query_params, headers, body):
      """ handle request for dl_styles.css """
      self.msg(f"_handle_dl_styles")
      return biplane.FileResponse("/www/dl_styles.css")

    # --- request-handler for /pure-min.css   -------------------------------

    @self._server.route("/pure-min.css","GET")
    def _handle_pure_min(query_params, headers, body):
      """ handle request for pure-min.css """
      self.msg(f"_handle_pure_min")
      return biplane.FileResponse("/www/pure-min.css")

    # --- request-handler for /config.html   ---------------------------------

    @self._server.route("/config.html","GET")
    def _handle_get_config(query_params, headers, body):
      """ handle request for config-page """
      self.msg(f"_handle_get_config")
      return biplane.FileResponse("/www/config.html")

    # --- request-handler for /save_config   ---------------------------------

    @self._server.route("/save_config","POST")
    def _handle_save_config(query_params, headers, body):
      """ handle request for /save_config """
      self.msg(f"_handle_save_config...\n{body}")
      self._export_config(body)
      return biplane.Response("<h1>configuration saved</h1>",
                              content_type="text/html")

  # --- import configuration   -----------------------------------------------

  def _import_config(self):
    """ import config-module and create json-model """
    import konfig           # TODO: change to config later after merge
    self._model = {}
    for var in dir(konfig):
      if var[0] != '_':
        if var in ["SENSORS", "TASKS"]:
          self._model[var] = getattr(konfig,var).split(" ")
        else:
          self._model[var] = getattr(konfig,var)
        self.msg(f"{var}={self._model[var]}")
    konfig = None
    gc.collect()


  # --- export configuration   -----------------------------------------------

  def _export_config(self,body):
    """ export json-model to config-module """

    # update model
    fields = body.decode().split("&")
    self.msg(f"{fields}")
    self._model['SENSORS'] = []
    self._model['TASKS'] = []
    self._model['HAVE_SD'] = False
    self._model['HAVE_LORA'] = False
    for field in fields:
      key,value = field.split("=")
      if '%' in value:
        value = self._html_decode(value)
      if key in ["SENSORS", "TASKS"]:
        self._model[key].append(value)
      elif key in ["have_sd", "have_lora"]:
        self._model[key.upper()] = True
      else:
        self._model[key] = value

    # dump to konfig (needs write access to flash -> boot.py)
    for key in self._model.keys():
      if key in ["SENSORS", "TASKS"]:
        print(f"{key}=\"{' '.join(self._model[key])}\"")
      else:
        print(f"{key}={self._html_decode(self._model[key])}")

  # --- decode html-escape chars   -------------------------------------------

  def _html_decode(self,text):
    """ decode html esc-chars (subset only!) """

    if not isinstance(text,str) or not '%' in text:
      return text
    token = text.split('%')
    result = token.pop(0)
    for t in token:
      decoded = chr(int(t[:2],16))
      result = f"{result}{decoded}{t[2:]}"
    return result

  # --- print message in debug-mode   ----------------------------------------

  def msg(self,text):
    if self._config["debug"]:
      print(f"{text}")

  # --- run server   ---------------------------------------------------------

  def run(self):
    """ run server in ap-mode """

    wifi.radio.stop_station()
    started = False
    for _ in self._server.circuitpython_start_wifi_ap(
      self._config["ssid"],
      self._config["password"],
      self._config["hostname"]):
      if not started:
        self.msg(f"Listening on http://{wifi.radio.ipv4_address_ap}:80")
        started = True
      gc.collect()
