#-----------------------------------------------------------------------------
# Gateway-task: save data to sd-card
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time

from log_writer import Logger
g_logger = Logger()

def run(config, app, msg_type, values):
  """ save data to sd-card """

  if not getattr(config,"HAVE_SD",False) and config.CSV_FILENAME[:7] != '/saves/':
    return

  # CSV filename formatting
  ts = time.localtime()
  ymd = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}"
  y,m,d = ymd.split("-")

  # extract LOGGER_ID from data
  lid_index = getattr(config,"CSV_FIELDNR_ID",1) # assume 2nd field is logger-id
  logger_id = values[lid_index]

  csv_file = config.CSV_FILENAME.format(ID=logger_id,
                                          GW_ID=config.GW_ID,
                                          YMD=ymd,Y=y,M=m,D=d)

  g_logger.print(f"gateway: saving data to {csv_file}...")
  with open(csv_file, "a") as f:
    f.write(f"{','.join(values)}\n")
