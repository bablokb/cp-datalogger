# -------------------------------------------------------------------------
# Run AP together with a web-server.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-examples
#
# -------------------------------------------------------------------------

import re
import gc
import sys
import os
import time
import json
import board
import wifi
import mdns
import socketpool
from ehttpserver import Server, Response, FileResponse, route

import commit
from pins import PCB_VERSION

# --- early configuration of the log-destination   ---------------------------

try:
  from log_config import g_logger
except:
  from log_writer import Logger
  g_logger = Logger('console')

from sensors.battery import BATTERY

# --- Webserver and Access-Point class   -------------------------------------

class WebAP(Server):
  """ Access-point and webserver """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config
    super().__init__(debug=config["debug"])
    self.debug("Initializing WebAP")
    self._import_config()

  # --- overwrite debug() from base class   -----------------------------------

  def debug(self,msg):
    """ route debug-messages to our logger """
    if self._debug:
      g_logger.print(msg)

  # --- request-handler for /   -----------------------------------------------

  @route("/","GET")
  def _handle_main(self,path,query_params, headers, body):
    """ handle request for main-page """
    g_logger.print("_handle_main...")
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
    g_logger.print(f"_handle_static for {path}")
    if self._config["cache"]:
      headers = {
        "Cache-Control": "max-age=2592000"
      }
    else:
      headers = {}
    return FileResponse(f"/www/{path}",headers=headers)

  # --- request-handler for /get_status_info   -------------------------------

  @route("/get_status_info","GET")
  def _handle_get_status_info(self,path,query_params, headers, body):
    """ handle request for /get_status_info """
    g_logger.print(f"_handle_get_status_info...")
    return Response(json.dumps(self._get_status()),
                    content_type="application/json")

  # --- request-handler for /get_model   -------------------------------------

  @route("/get_model","GET")
  def _handle_get_model(self,path,query_params, headers, body):
    """ handle request for /get_model """
    g_logger.print(f"_handle_get_model...")
    return Response(json.dumps(self._model),content_type="application/json")

  # --- request-handler for /get_csv_list   ----------------------------------

  @route("/get_csv_list","GET")
  def _handle_get_csv_list(self,path,query_params, headers, body):
    return self._handle_get_file_list(path,query_params, headers, body)

  # --- request-handler for /get_log_list   ----------------------------------

  @route("/get_log_list","GET")
  def _handle_get_file_list(self,path,query_params, headers, body):
    return self._handle_get_file_list(path,query_params, headers, body)

  # --- implementing handler for csv/log lists   -----------------------------

  def _handle_get_file_list(self,path,query_params, headers, body):
    """ handle requests for /get_xxx_list """
    g_logger.print(f"_handle_get_file_list...")
    ftype = f".{path.split('_')[1]}"
    response = json.dumps({
      "files":
      sorted([fname for fname in os.listdir("/sd") if fname[-4:] == ftype],
             reverse=True)
        })
    self.debug(f"{response=}")
    return Response(response,content_type="application/json")

  # --- request-handler for /save_config   -----------------------------------

  @route("/save_config","POST")
  def _handle_save_config(self,path,query_params, headers, body):
    """ handle request for /save_config """
    g_logger.print(f"_handle_save_config...\n{body}")
    try:
      self._export_config(body)
      return Response("configuration saved",
                      content_type="text/plain")
    except Exception as ex:
      g_logger.print(f"exception during save_config: {ex}")
      return Response("could not save configuration",
                      content_type="text/plain")

  # --- request-handler for /set_time   --------------------------------------

  @route("/set_time","POST")
  def _handle_set_time(self,path,query_params, headers, body):
    """ handle request for /set_time """
    g_logger.print(f"_handle_set_time...\n{body}")
    try:
      _,new_time = body.decode().split("=")
      if self._config["rtc"]:
        self._config["rtc"].update(int(new_time))
      return Response(json.dumps(self._get_status()),
                      content_type="application/json")
    except Exception as ex:
      g_logger.print(f"exception updating time: {ex}")
      return Response("could not update time",
                      content_type="text/plain")

  # --- request-handler for config.py download   -----------------------------

  @route("/config.py","GET")
  def _handle_download_config_py(self,path,query_params, headers, body):
    """ handle request for config.py download """
    g_logger.print(f"_handle_download_config_py")
    return FileResponse(f"config.py",content_type="application/octet-stream")

  # --- request-handler for config.py upload   -------------------------------

  @route("/upload_config","POST")
  def _handle_upload_config_py(self,path,query_params, headers, body):
    """ handle request for config.py upload """
    g_logger.print(f"_handle_upload_config_py...\n{body}")

    try:
      with open("config.py","wb") as file:
        file.write(body)
      self._import_config()
      return Response("config.py uploaded successfully",
                      content_type="text/plain")
    except Exception as ex:
      g_logger.print(f"exception during update of config.py: {ex}")
      return Response("config.py upload failed",
                      content_type="text/plain")

  # --- request-handler for csv/log-files   ----------------------------------

  @route("/[^.]+\.(csv|log)","GET")
  def _handle_file_download(self,path,query_params, headers, body):
    """ handle request for file-download """
    g_logger.print(f"_handle_file_download for {path}")
    return FileResponse(f"/sd/{path}",
                        content_type="application/octet-stream",
                        buffer_size=4096)

  # --- request-handler for csv/log-delete   ---------------------------------

  @route("/[^.]+\.(csv|log).delete","GET")
  def _handle_file_delete(self,path,query_params, headers, body):
    """ handle request for file-delete """
    g_logger.print(f"_handle_file_delete for {path}")
    try:
      os.remove(f"/sd/{path[0:-7]}")
    except:
      return Response(f"delete failed for {path[0:-7]}",status_code=400,
                      content_type="text/plain")
    return Response(f"successfully deleted {path[0:-7]}",
                                content_type="text/plain")

  # --- get system status   --------------------------------------------------

  def _get_status(self):
    """ get system status """
    bat = BATTERY(None,None)
    status = {"lipo": getattr(self._model,"HAVE_LIPO",False)}
    bat.read(status,[])
    v = sys.implementation[1]
    status.update({
      "board_id": board.board_id,
      "pcb_version": PCB_VERSION,
      "cp_version": f"{v[0]}.{v[1]}.{v[2]}",
      "dl_commit" : commit.commit,
      "dev_time": time.time()
      })
    g_logger.print(f"{status=}")
    return status

  # --- read lines from config.py   ------------------------------------------

  def _next_config_line(self):
    """ read next line from config.py """

    with open("config.py","r") as file:
      next_line = ""
      for line in file:
        if line[0] in ['#','\n']:
          continue
        line = line.strip('\n')
        # remove comment
        c = line.rfind('#')
        if c > -1:
          line = line[:c]
        line = line.strip(' ')
        if not '=' in line:
          # must be a continuation-line
          next_line += line
          continue
        parts = line.split('=')
        if len(parts) == 1:
          # first part of a continuation line
          next_line = part[0]
          continue
        else:
          # return next_line if already set
          if next_line:
            yield next_line
          next_line = line
      if next_line:
        yield next_line

  # --- import configuration   -----------------------------------------------

  def _import_config(self):
    """ import config-module and create json-model """

    self._model = {}
    try:
      for line in self._next_config_line():
        var, value = line.split('=')
        # strip blanks and quotes from var/value
        var   = var.strip(' ')
        value = value.strip(' ')
        if value[0] in ["'",'"']:          # prevent stripping from f-string
          value = value.strip("'\"")
        elif value in ["True","False"]:
          value = True if value == "True" else False
        if var in ["SENSORS", "TASKS"]:
          self._model[var] = value.split(" ")
        elif var == 'TIME_TABLE':
          self._model[var] = json.loads(
            value.replace('(','[').
            replace(')',']').
            replace('None','null')
          )
        else:
          self._model[var] = value
    except Exception as ex:
      g_logger.print(f"exception: {ex}")
      g_logger.print("could not read config.py")
    gc.collect()
    self._dump_model()

    # add select-options for sensors and tasks
    self._model["_s_options"] = [f.split(".")[0] for f in os.listdir("sensors")]
    self._model["_t_options"] = [f.split(".")[0] for f in os.listdir("tasks")]
    self.debug(f"sensor options: {self._model['_s_options']}")
    self.debug(f"task options:   {self._model['_t_options']}")

  # --- dump model   ---------------------------------------------------------

  def _dump_model(self):
    """ dump model """

    self.debug("-"*60)
    self.debug("model:")
    self.debug("-"*60)
    for key in sorted(self._model.keys()):
      if key[0] == "_":
        continue
      value = self._model[key]
      self.debug(f"{key}={value}")
    self.debug("-"*60)

  # --- check for number   ---------------------------------------------------

  def _is_num(self,txt):
    """ check text for numbers """
    return re.match("^-?[.0-9]+$",txt)  # optional -, then only . and numbers

  # --- export configuration   -----------------------------------------------

  def _export_config(self,body):
    """ export json-model to config-module """

    # update model
    fields = body.decode().split("&")
    self.debug(f"{fields}")
    self._model['SENSORS'] = ""
    self._model['TASKS'] = ""
    self._model['HAVE_SD'] = False
    self._model['HAVE_LIPO'] = False
    self._model['HAVE_LORA'] = False

    self._model['TIME_TABLE'] = [(None,None) for i in range(7)]
    tt_day_keys = [f"d_{i}" for i in range(7)]
    tt_day_vals = [False for i in range(7)]
    tt_keys = [f"{scale}{typ}_{i}" for i in range(7)
               for typ in 'sei' for scale in 'hm']
    tt_vals = [[[0,0,0],[0,0,0]] for i in range(7)]

    for field in fields:
      key,value = field.split("=")
      if '%' in value or '+' in value:
        value = self.html_decode(value).strip(" ")
      if key in ["HAVE_SD", "HAVE_LIPO", "HAVE_LORA"]:
        # checkboxes send key="on" if checked, else nothing at all
        self._model[key] = True
      elif key in tt_day_keys:
        day = int(key[-1:])
        tt_day_vals[day] = True
      elif key in tt_keys:
        scale = 'hm'.index(key[0])
        typ   = 'sei'.index(key[1])
        day   = int(key[3])
        tt_vals[day][scale][typ] = int(value) if value else 0
      else:
        self._model[key] = value

    # fix sensors and tasks
    for key in ["SENSORS", "TASKS"]:
      self._model[key] = self._model[key].split()

    # fix time-table
    have_time_table = False
    for day in range(7):
      if not tt_day_vals[day]:
        continue
      have_time_table = True
      self._model['TIME_TABLE'][day] = tt_vals[day]
    if not have_time_table:
      del self._model['TIME_TABLE']

    # dump model
    self._dump_model()

    # write to config.py (needs write access to flash -> boot.py)
    # (dump SENSORS as first variable for reuse in other variables)
    try:
      g_logger.print("writing config.py...")
      keys = ["SENSORS"] + [key for
        key in sorted(self._model.keys()) if key[0] != "_" and key != "SENSORS"]
      with open("config.py","w") as file:
        file.write("# generated from admin-mode web-interface\n\n")
        for key in keys:
          value = self._model[key]
          if key in ["SENSORS", "TASKS"]:
            file.write(f"{key}=\"{' '.join(value)}\"\n")
          elif type(value) in [int,float,bool,list]:
            file.write(f"{key}={value}\n")
          elif value in ["True","False","None"]:
            file.write(f"{key}={value}\n")
          elif self._is_num(value) and (
            len(value) == 1 or value[0] != "0" or '.' in value):
            file.write(f"{key}={value}\n")
          elif value[0] == 'f':               # dump f-strings literally
            file.write(f"{key}={value}\n")
          else:
            file.write(f"{key}=\"{value}\"\n")
      g_logger.print("...done")
    except Exception as ex:
      g_logger.print(f"exception: {ex}")
      g_logger.print(f"error writing config.py")

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
    g_logger.print(f"starting {server.hostname}.local ({wifi.radio.ipv4_address_ap})")
    with pool.socket() as server_socket:
      yield from self.start(server_socket)

  # --- run AP and server   --------------------------------------------------

  def run(self):
    """ start AP and then run server """
    self.start_ap()
    started = False
    for _ in self.run_server():
      if not started:
        g_logger.print(f"Listening on http://{wifi.radio.ipv4_address_ap}:80")
        started = True
      gc.collect()
