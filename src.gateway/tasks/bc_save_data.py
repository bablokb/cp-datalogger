#-----------------------------------------------------------------------------
# Gateway-task: save broadcast-info to sd-card
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time

from log_writer import Logger
g_logger = Logger()

def run(config, app, values):
  """ save broadcast-info to sd-card """

  if not getattr(config,"HAVE_SD",False):
    return
  filename = getattr(config,"BCAST_CSV_FILENAME","/sd/bcast_{GW_ID}_{ID}.csv")

  # CSV filename formatting
  ts = time.localtime()
  ymd = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}"
  y,m,d = ymd.split("-")

  # data: [rc,TS,ID,pnr,node]

  # extract LOGGER_ID from data
  logger_id = values[2]

  csv_file = filename.format(ID=logger_id,
                             GW_ID=config.GW_ID,
                             YMD=ymd,Y=y,M=m,D=d)

  g_logger.print(f"gateway: saving bcast-info to {csv_file}...")
  with open(csv_file, "a") as f:
    f.write(f"{','.join(values)}\n")
