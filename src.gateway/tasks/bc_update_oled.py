#-----------------------------------------------------------------------------
# Gateway-task: show broadcast-info on OLED
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config, app, msg_type, values):
  """ display broadcast-information """

  if not (getattr(config,"HAVE_OLED",False) and app.oled):
    return
  if msg_type != "B":
    g_logger.print(f"gateway: bc_upd_oled: illegal msg_type: {msg_type}")
    return

  # data: [TS,ID,pnr,node,rc,snr,rssi,sf,cr,bw,duration]
  rc = values[4] == '1'
  app.update_oled([values[0],
                   f"ID/N:{values[1]}/{values[3]}: {values[2]} {'+' if rc else '-'}",
                   f"Q: {values[5]}, {values[6]} dBm",
                   f"t: {values[-1]}s"]
                  )
