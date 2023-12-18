# -------------------------------------------------------------------------
# Run AP together with a web-server.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import gc
import os
import json
import board
import wifi
import mdns
import socketpool
from ehttpserver import Server, Response, FileResponse, route

class WebAP(Server):
  """ Access-point and webserver """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config
    super().__init__(debug=config["debug"])
    self.debug("Initializing WebAP")
    self._import_config()

  # --- request-handler for /   -----------------------------------------------

  @route("/","GET")
  def _handle_main(self,path,query_params, headers, body):
    """ handle request for main-page """
    self.debug("_handle_main...")
    return FileResponse("/www/index.html")

  # --- request-handler for /favicon.ico   -----------------------------------

  @route("/favicon.ico","GET")
  def _handle_favicon(self,path,query_params, headers, body):
    """ handle request for favicon """
    self.debug("_handle_favicon...")
    return Response("",status_code=400)

  # --- request-handler for static files   -----------------------------------

  @route("/[^.]*\.(js|css|html)","GET")
  def _handle_static(self,path,query_params, headers, body):
    """ handle request for static-files """
    self.debug(f"_handle_static for {path}")
    return FileResponse(f"/www/{path}")

  # --- request-handler for /get_model   -------------------------------------

  @route("/get_model","GET")
  def _handle_get_model(self,path,query_params, headers, body):
    """ handle request for /get_model """
    self.debug(f"_handle_get_model...")
    return Response(json.dumps(self._model),content_type="application/json")

  # --- request-handler for /get_csv_list   ----------------------------------

  @route("/get_csv_list","GET")
  def _handle_get_csv_list(self,path,query_params, headers, body):
    """ handle request for /get_csv_list """
    self.debug(f"_handle_get_csv_list...")
    response = json.dumps({
        "files": [csv for csv in os.listdir("/sd") if csv[-4:] == ".csv"]
        })
    self.debug(f"{response=}")
    return Response(response,content_type="application/json")

  # --- request-handler for /save_config   -----------------------------------

  @route("/save_config","POST")
  def _handle_save_config(self,path,query_params, headers, body):
    """ handle request for /save_config """
    self.debug(f"_handle_save_config...\n{body}")
    self._export_config(body)
    return Response("<h1>configuration saved</h1>",
                                content_type="text/html")

  # --- request-handler for config.py download   -----------------------------

  @route("/config.py","GET")
  def _handle_download_config_py(self,path,query_params, headers, body):
    """ handle request for config.py download """
    self.debug(f"_handle_download_config_py")
    return FileResponse(f"config.py",content_type="application/octet-stream")

  # --- request-handler for config.py upload   -------------------------------

  @route("/upload_config","POST")
  def _handle_upload_config_py(self,path,query_params, headers, body):
    """ handle request for config.py upload """
    self.debug(f"_handle_upload_config_py...\n{body}")

    return Response("<h1>config.py upload not implemented yet</h1>",
                                content_type="text/html")

  # --- request-handler for csv-files   ---------------------------------------

  @route("/[^.]+\.csv","GET")
  def _handle_csv_download(self,path,query_params, headers, body):
    """ handle request for csv-download """
    self.debug(f"_handle_csv_download for {path}")
    return FileResponse(f"/sd/{path}")

  # --- import configuration   -----------------------------------------------

  def _import_config(self):
    """ import config-module and create json-model """

    import config
    self.debug("-"*60)
    self.debug("current config.py:")
    self.debug("-"*60)

    self._model = {}
    for var in dir(config):
      if var[0] != '_':
        if var in ["SENSORS", "TASKS"]:
          self._model[var] = getattr(config,var).split(" ")
        else:
          self._model[var] = getattr(config,var)
        self.debug(f"{var}={self._model[var]}")
    config = None
    gc.collect()
    self.debug("-"*60)

    # add select-options for sensors and tasks
    self._model["_s_options"] = [f.split(".")[0] for f in os.listdir("sensors")]
    self._model["_t_options"] = [f.split(".")[0] for f in os.listdir("tasks")]
    self.debug(f"sensor options: {self._model['_s_options']}")
    self.debug(f"task options:   {self._model['_t_options']}")

  # --- export configuration   -----------------------------------------------

  def _export_config(self,body):
    """ export json-model to config-module """

    # update model
    fields = body.decode().split("&")
    self.debug(f"{fields}")
    self._model['SENSORS'] = []
    self._model['TASKS'] = []
    self._model['HAVE_SD'] = False
    self._model['HAVE_LORA'] = False
    for field in fields:
      key,value = field.split("=")
      if '%' in value:
        value = self.html_decode(value)
      if key in ["SENSORS", "TASKS"]:
        self._model[key].append(value)
      elif key in ["have_sd", "have_lora"]:
        self._model[key.upper()] = True
      else:
        self._model[key] = value

    # dump to config (needs write access to flash -> boot.py)
    self.msg("writing config.py...")
    with open("config.py","w") as file:
      file.write("# generated from admin-mode web-interface\n\n")
      for key in sorted(self._model.keys()):
        if key[0] == "_":
          continue
        value = self._model[key]
        if key in ["SENSORS", "TASKS"]:
          file.write(f"{key}=\"{' '.join(value)}\"\n")
        elif type(value) in [int,float,bool,list]:
          file.write(f"{key}={value}")
        elif value in ["True","False"]:
          file.write(f"{key}={value}\n")
        elif value.isdigit() and (value[0] != "0" or len(value) == 1):
          file.write(f"{key}={value}\n")
        else:
          file.write(f"{key}=\"{value}\"\n")
    self.msg("...done")

  # --- run AP   -------------------------------------------------------------

  def start_ap(self):
    """ start AP-mode """

    wifi.radio.stop_station()
    try:
      wifi.radio.start_ap(ssid=self._config["ssid"],
                          password=self._config["password"])
    except NotImplementedError:
      # workaround for older CircuitPython versions
      pass

  # --- run server   ---------------------------------------------------------

  def run_server(self):

    server = mdns.Server(wifi.radio)
    server.hostname = self._config["hostname"]
    server.advertise_service(service_type="_http",
                             protocol="_tcp", port=80)
    pool = socketpool.SocketPool(wifi.radio)
    self.debug(f"starting {server.hostname}.local ({wifi.radio.ipv4_address_ap})")
    with pool.socket() as server_socket:
      yield from self.start(server_socket)

  # --- run AP and server   --------------------------------------------------

  def run(self):
    """ start AP and then run server """
    self.start_ap()
    started = False
    for _ in self.run_server():
      if not started:
        self.debug(f"Listening on http://{wifi.radio.ipv4_address_ap}:80")
        started = True
      gc.collect()
