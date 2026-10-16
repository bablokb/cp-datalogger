#-----------------------------------------------------------------------------
# Configuration constants for main.py.
#
# Example using a Pimoroni Badger2350 (with /saves partition).
# This configuration assumes that a SEN6x is attached to the Stemma/Qt
# connector of the Badger2350.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

NET_UPDATE  = True        # update RTC from time-server if time is invalid

STROBE_MODE = False
INTERVAL    = 60

# sample once every five minutes from 08:00 to 19:55
# TIME_TABLE = [
#   ((8,19,1),(0,59,5)),
#   ((8,19,1),(0,59,5)),
#   ((8,19,1),(0,59,5)),
#   ((8,19,1),(0,59,5)),
#   ((8,19,1),(0,59,5)),
#   ((8,19,1),(0,59,5)),
#   ((8,19,1),(0,59,5))
#   ]

HAVE_SD       = False
HAVE_DISPLAY  = "internal"
HAVE_RTC      = "PCF85063(0)"
HAVE_I2C0     = True
HAVE_PM       = False
HAVE_LIPO     = True

SENSORS      = "id dcode battery sen6x"
ALTITUDE_AT_LOCATION = 540                  # correct for altitude

CSV_HEADER_EXTENDED = True
CSV_FILENAME = f'/saves/data-{{ID}}-{SENSORS.replace(' ','_')}.csv'

LOGGER_NAME  = 'badger2350'
LOGGER_ID    = '2350_1'
LOGGER_LOCATION = '@Home'
LOGGER_TITLE    = "CO2/T/Hum @ Home"

FONT_DISPLAY = "DejaVuSansMono-Bold-16-subset"
SEN6X_SAMPLES = 2                           # in continuous mode
SEN6X_PROPERTIES = "c t h pm25 pm40"   # show on display
SEN6X_FORMATS = {
  "c":    ["C:", "{0}p"],          # 0 - 40000
  "t":    ["T:", "{0:.1f}°C"],
  "h":    ["H:", "{0:.0f}%rH"],

  "voc":  ["VOC:","{0}"],          # 1 - 500
  "nox":  ["NOX:","{0}"],          # 1 - 500

  "pm10":  ["PM1.0:","{0}"],       # 0 - 1000 µg/m³
  "pm25":  ["PM2.5:","{0}"],       # 0 - 1000 µg/m³
  "pm40":  ["PM4.0:","{0}"],       # 0 - 1000 µg/m³
  "pm100": ["PM10:","{0}"],        # 0 - 1000

  "pn10":  ["PN1.0:","{0:0.1f}"],  # 0 - 6554 particles/cm³
  "pn25":  ["PN2.5:","{0:0.1f}"],  # 0 - 6554 particles/cm³
  "pn40":  ["PN4.0:","{0:0.1f}"],  # 0 - 6554 particles/cm³
  "pn100": ["PN10:","{0:0.1f}"],   # 0 - 6554 particles/cm³
  }


# tasks to execute after data-collection
TASKS = "dump_data save_data update_display"
