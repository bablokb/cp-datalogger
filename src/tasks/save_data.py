#-----------------------------------------------------------------------------
# Task: save data to sd-card
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config,app):
  """ save data to sd-card """

  if not config.HAVE_SD:
    return

  ymd = app.data["ts_str"].split("T")[0]
  y,m,d = ymd.split("-")
  outfile = config.CSV_FILENAME.format(
    ID=config.LOGGER_ID,
    YMD=ymd,Y=y,M=m,D=d)
  new_csv = not app.file_exists(outfile)
  app.save_status = ":("
  with open(outfile, "a") as f:
    if new_csv:
      f.write(f"{app.csv_header}\n")
    f.write(f"{app.record}\n")
    app.save_status = "SD"
