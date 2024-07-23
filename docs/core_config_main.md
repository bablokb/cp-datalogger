Main Datalogger Configuration
=============================

Logger-Identification
---------------------

| Name              | Type | O/M | Description                 |
|-------------------|------|-----|-----------------------------|
| LOGGER_NAME       | str  |  M  | Name of the logger          |
| LOGGER_ID         | str  |  M  | ID of the logger            |
| LOGGER_LOCATION   | str  |  M  | Location, e.g. plus-code    |
| LOGGER_TITLE      | str  |  O  | Default: ID: NAME           |


CSV-File
--------

| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| CSV_FILENAME        | str  |  O  | CSV filename. Details below.|
| CSV_HEADER_EXTENDED | bool |  O  | Write extended header       |

`CSV_FILENAME` must start with  `/sd/`.

The name of the generated CSV-file can be dynamic. The following
placeholders are possible:

  - `{ID}`: the `LOGGER_ID`
  - `{YMD}`: the date in the format `yyyy-mm-dd`
  - `{Y}`: the year in the format `yyyy`
  - `{M}`: the month in the format `mm`
  - `{D}`: the day in the format `dd`

`CSV_HEADER_EXTENDED` will write additional header lines:

    #  nr: header

for all columns in the CSV. A normal header line

    #h0,h1,...,h<n>

is always written, regardless of the value of `CSV_HEADER_EXTENDED`.


Sensors
-------

| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| SENSORS             | str  |  M  | list of sensors             |
| SENSORS_CSV_ONLY    | str  |  O  | sensors not for the display |

`SENSORS` is a blank delimted string with sensor specifications.
Each An entry must be any of (no spaces allowed!):

  - sensor
  - sensor(bus)  
    bus = 0|1
  - sensor(addr) 
    addr = 0x..
  - sensor(addr,bus)

When no bus is provided, busses are probed in the order i2c1,i2c0.
When no address is provided, the default address as configured in
the driver is used. `addr` **must** have a leading `0x`.

Since the display can only show 6 values, you can exclude sensors
from the display. The data is still recorded in the CSV.
Entries in 'SENSORS_CSV_ONLY' must match exactly to entries in 'SENSORS'.


Tasks
-----

| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| TASKS               | str  |  M  | List of tasks               |

List of tasks to execute. This is a blank delimeted list. See
[tasks](./tasks.md) for a list of available tasks and task-specific
configuration.


Time Updates
------------


| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| NET_UPDATE          | bool |  O  | update time from time-server|
| SAVE_WAKEUP         | bool |  O  | save/restore wakeup time    |

`SAVE_WAKEUP` is a workaround for buggy batteries. The system
saves the wakeup time on SD-card and restores the time after the
next boot in case the time is invalid and cannot be updated
from a time-server.


Sample-Mode and Intervals
-------------------------


| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| STROBE_MODE         | bool |  O  | continuous or strobe mode   |
| INTERVAL            | int  |  O  | interval in cont. mode      |
| TIME_TABLE          |      |  O  | time-table                  |

In `STROBE_MODE`, the system cuts power after data
collection. Otherwise, the system will use deep-sleep (light-sleep for
intervals shorter than 60 seconds). Without available power-management
(see `HAVE_PM` below), the system uses deep-sleep as a fallback even
in strobe-mode.

`INTERVAL` is the time-period between samples. `INTERVAL` is ignored
if you define a time-table. The default value for `INTERVAL` is
900 seconds (i.e. 15 minutes).

A time-table is a list with one entry per day, starting with Monday.
For every day, two tuples define the hours and minutes when sampling
takes place.

A formal definition of an entry is:

    ((h_start,h_end,h_inc),(m_start,m_end,m_inc))

Start and end values are inclusive. The time-table

    ((7,18,1),(0,59,15)),
    ((7,18,1),(0,59,15)),
    ((7,18,1),(0,59,15)),
    ((7,18,1),(0,59,15)),
    ((7,18,1),(0,59,15)),
    (None,None),
    (None,None)
    ]

will wake up the system Mo-Fr from 07:00-18:45 every 15 minutes.


Hardware Setup
--------------

| Name                | Type | O/M | Description                          |
|---------------------|------|-----|--------------------------------------|
| HAVE_PM             | bool |  O  | have power-management (True)         |
| SHUTDOWN_HIGH       | bool |  O  | shutdown on high-transition (True)   |
| HAVE_RTC            | str  |  O  | type and bus (def: PCF8523(1))       |
| HAVE_SD             | bool |  O  | support SD (True)                    |
| HAVE_I2C0           | bool |  O  | also use I2C0 (False)                |
| HAVE_LIPO           | bool |  O  | use LiPo (False)                     |
| HAVE_DISPLAY        | str  |  O  | name of the display (see below)      |
| FONT_DISPLAY        | str  |  O  | font for the display (see below)     |
| HAVE_LORA           | bool |  O  | support LoRa (RFM9x)                 |
| HAVE_OLED           | str  |  O  | support I2C-OLED                     |

Valid values for `HAVE_RTC` (`bus`: `0` or `1`):

  - "PCF8523(bus)"
  - "PCF8563(bus)"
  - "PCF85063(bus)"

See [task configuration](./core_config_tasks.md) for details about
`HAVE_DISPLAY`, `FONT_DISPLAY`, `HAVE_LORA` and `HAVE_OLED`. 


Development/Test
----------------

| Name                | Type | O/M | Description                     |
|---------------------|------|-----|---------------------------------|
| TEST_MODE           | bool |  O  | switch dev-features on (False)  |
| BLINK_START         | int  |  3  | blink before data-sampling      |
| BLINK_TIME_START    | float| 0.5 | blink duration before sammpling |
| BLINK_END           | int  |  5  | blink after data-sampling       |
| BLINK_TIME_END      | float| 0.25| blink duration after sampling   |

Test-mode writes a lot of additional information to the console and
is therefore not useful if not connected to a console. It also slows
down sampling.

Blinking takes place before and after sensor-readout, but only in
test-mode. It blinks the LED on the Pico(W)-PCB, which is usually
not visible except in a lab-environment.
