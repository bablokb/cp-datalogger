#-----------------------------------------------------------------------------
# Gateway-task: save broadcast data to sd-card
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time

from log_writer import Logger
g_logger = Logger()

def run(config, app, msg_type, values):
  """ save broadcast-info to sd-card """

  fname = getattr(config,"BCAST_CSV_FILENAME","/sd/bcast_{GW_ID}_{ID}.csv")
  if not getattr(config,"HAVE_SD",False) and fname[:7] != "/saves/":
    return

  if msg_type != "B":
    g_logger.print(f"gateway: bc_save_data: illegal msg_type: {msg_type}")
    return

  # CSV filename formatting
  ts = time.localtime()
  ymd = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}"
  y,m,d = ymd.split("-")

  # data: [TS,ID,pnr,node,rc,snr,rssi,sf,cr,bw,duration]

  # extract LOGGER_ID from data
  logger_id = values[1]

  csv_file = fname.format(ID=logger_id,
                             GW_ID=config.GW_ID,
                             YMD=ymd,Y=y,M=m,D=d)

  g_logger.print(f"gateway: saving broadcast data to {csv_file}...")
  with open(csv_file, "a") as f:
    f.write(f"{','.join(values)}\n")
