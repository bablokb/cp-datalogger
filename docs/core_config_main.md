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
Each entry must be in **lowercase** and in any of the
following formats (no spaces allowed!):

  - sensor
  - sensor(bus)  
    bus = 0, 1, ... (higher numbers with I2C-multiplexers)
  - sensor(addr) 
    addr = 0x..
  - sensor(addr,bus)

For a list of available sensors, see [sensors](./sensors.md).

When no bus is provided, busses are probed in the order i2c0,i2c1
(i2c0 only if `HAVE_I2C0=True` below).  When no address is provided,
the default address as configured in the driver is used. `addr`
**must** have a leading `0x`.

Since the display can only show 6 values, you can exclude sensors
from the display. The data is still recorded in the CSV.
Entries in 'SENSORS_CSV_ONLY' must match exactly to entries in 'SENSORS'.


Tasks
-----

| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| TASKS               | str  |  M  | List of tasks               |

List of tasks to execute. This is a blank delimeted list. See
[tasks](./tasks.md) for a list of available tasks and also check
[task-specific configuration](./core_config_tasks.md).


Time Updates
------------


| Name                | Type | O/M | Description                 |
|---------------------|------|-----|-----------------------------|
| NET_UPDATE          | bool |  O  | update time from time-server|
| SAVE_WAKEUP         | bool |  O  | save/restore wakeup time    |

`NET_UPDATE` defaults to `False` since there is no time-server
available any more that can be used without an API-key.

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
intervals shorter than 61 seconds). Without available power-management
(see `HAVE_PM` below), the system uses deep-sleep as a fallback even
in strobe-mode.

`INTERVAL` is the time-period between samples. **`INTERVAL` is ignored
if you define a time-table**. The default value for `INTERVAL` is
900 seconds (i.e. 15 minutes).

Using `INTERVAL=0` will sample the sensors as fast as possible.
Depending on the specific sensors, this can be as low as once every
second with a RP2040.

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

Note that time-table based wakeup will only work if either the
PM-circuitry supports wake by RTC-alarm, or in continuous-mode
(i.e. `STROBE_MODE=False`).  In the latter case, the behaviour depends
on the precision of the internal RTC, which is usually not great
(the internal RTC of the RP2040 is off by about 8s per day).


Hardware Setup
--------------

| Name                | Type | O/M | Description                          |
|---------------------|------|-----|--------------------------------------|
| HAVE_PM             | bool |  O  | have power-management (True)         |
| SHUTDOWN_HIGH       | bool |  O  | shutdown on high-transition (True)   |
| HAVE_RTC            | str  |  O  | type and bus (def: PCF8523(1))       |
| HAVE_SD             | bool |  O  | support SD (True)                    |
| HAVE_I2C0           | bool |  O  | also use I2C0 (False)                |
| HAVE_I2C_MP         | str  |  O  | I2C-multiplexer definition (None)    |
| HAVE_LIPO           | bool |  O  | use LiPo (False)                     |
| HAVE_DISPLAY        | str  |  O  | name of the display (see below)      |
| FONT_DISPLAY        | str  |  O  | font for the display (see below)     |
| HAVE_LORA           | bool |  O  | support LoRa (RFM9x)                 |
| HAVE_OLED           | str  |  O  | support I2C-OLED                     |
| BTN_A_CODEFILE      | str  |  O  | run-file for button A (admin.py)     |
| BTN_A_FLASH_RW      | bool |  O  | remount flash rw (True)              |
| BTN_B_CODEFILE      | str  |  O  | run-file for button B (broadcast.py) |
| BTN_B_FLASH_RW      | bool |  O  | remount flash rw (False)             |
| BTN_C_CODEFILE      | str  |  O  | run-file for button C (bootloader.py)|
| BTN_C_FLASH_RW      | bool |  O  | remount flash rw (False)             |

Valid values for `HAVE_RTC`:

  - None
  - "PCF8523(bus)"
  - "PCF8563(bus)"
  - "PCF85063(bus)"

`bus` must be a valid bus-number, usually `0` or `1` except if you
attach the RTC to an IC2-multiplexer (see below).

I2C-multiplexers are supported using `HAVE_I2C_MP`. The format is

    HAVE_I2C_MP = "spec1 spec2 ..."

where each specification is `chip(bus[,addr])`. Currently, only chips
that are implemented by the TCA9548A-library are supported, i.e.
PCA9546A, PCA9548A, TCA9546A and TCA9548A (you can ommit the trailing
'A').

The `bus`-parameter *must* be `0` or `1`. The optional address
defaults to `0x70` and must be specified in hex-notation if not
omitted.

Every multiplexer will add 4 or 8 I2C-channels. When defining sensors,
the bus-number will start at 2 and will then increment according to
the multiplexer used. E.g. when adding a 4 channel and an 8 channel
multiplexer, the bus-numbers will be 2-5 and 6-13.

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
