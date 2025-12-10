#-----------------------------------------------------------------------------
# Gateway-task: show broadcast-info on OLED
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config, app, values):
  """ display broadcast-information """

  if not (getattr(config,"HAVE_OLED",False) and app.oled):
    return
  else:
    # data: [rc,TS,ID,pnr,node]
    rc = values[0]
    app.update_oled([values[1],
                     f"ID/N:{values[2]}/{values[4]}: {values[3]}",
                     "OK" if rc else "FAILED"]
                    )
