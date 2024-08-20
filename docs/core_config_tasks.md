Task Specific Configuration
===========================

dump_data
---------

| Name                        | Type | O/M | Description                    |
|-----------------------------|------|-----|--------------------------------|
| SHOW_UNITS                  | bool |  O  | print values to console or log |

With `SHOW_UNITS = True` (default), sensor values are printed to the log
in pseudo-tabular form with units.

`SHOW_UNITS = False` will print directly in CSV-format to the serial console
(even if logging is redirected or disabled).


update_display
--------------

| Name                  | Type | O/M | Description                       |
|-----------------------|------|-----|-----------------------------------|
| HAVE_DISPLAY          | str  |  O  | display-name (see below)          |
| FONT_DISPLAY          | str  |  O  | font-name (see below)             |
| SIMPLE_UI             | bool |  O  | show simple UI (False)            |
| DISPLAY_STROBE_WAIT   | int  |  O  | extra update time (3)             |
| DISPLAY_LAYOUT_RC     | bool |  O  | layout is row-column order (True) |
| DISPLAY_LAYOUT_MAXDIM | str  |  O  | max layout dimensions (RxC = 3x4) |

Valid values for `HAVE_DISPLAY`:

  - None (default)
  - "internal" (uses `board.DISPLAY`)
  - "Inky-Pack" (Pimoroni Inky-Pack e-Ink display)
  - "Inky-pHat" (Pimoroni Inky-pHat e-Ink display)
  - "Display-Pack" (Pimoroni Display-Pack, needs `HAVE_SD=False`)
  - "Ada-2.13-Mono" (Adafruit 2.13 Mono e-Ink display)
  - "Ada-1.54-Mono" (Adafruit 1.54 Mono e-Ink display)

Valid values for `FONT_DISPLAY`:

  - DejaVuSans-16-subset
  - DejaVuSansMono-12-subset
  - DejaVuSansMono-Bold-16-subset
  - DejaVuSansMono-Bold-18-subset (default)

If `SIMPLE_UI` is true, only a minimalistic (label-based) UI is shown.
This is much faster than the default tabular UI.

The layout of the tabular UI is dynamic with at most three rows and
four columns. Use `DISPLAY_LAYOUT_MAXDIM` to change the default.  Note
that larger layouts use more memory. Values that don't fit into the
layout will still be written to the CSV-file. Most sensors allow the
configuration of properties that are displayed.

`DISPLAY_STROBE_WAIT` will give the e-ink some extra time for updates
before the power-management cuts power in strobe-mode.


send_lora
---------

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| HAVE_LORA                   | bool |  O  | support LoRa (RFM9x)      |
| LORA_FREQ                   | float|  M  | 433 / 868 / 915           |
| LORA_BASE_ADDR              | int  |  O  | gateway-address (def: 0)  |
| LORA_NODE_ADDR              | int  |  M  | node-address              |
| LORA_ENABLE_TIME            | float|  O  | enable wait-time (0)      |
| LORA_ACK_WAIT               | float|  O  | wait for ACK time (0.25)  |
| LORA_ACK_RETRIES            | int  |  O  | send retries (3)          |
| LORA_TX_POWER               | int  |  O  | transmit power (5-23)     |

Default transmit power is 13.


update_oled
-----------

| Name         | Type | O/M | Description                           |
|--------------|------|-----|---------------------------------------|
| HAVE_OLED    | str  |  O  | support I2C-OLED (default: None)      |
| OLED_TIME    | int  |  O  | show OLED at least the given time (3) |
| OLED_VALUES  | str  |  O  | see below                             |

Valid values for `HAVE_OLED` is `None` or `"bus,addr,width,height"`.
`bus` can be either `*`, which will probe all available busses, or an
integer bus number. Providing an explicit bus-number is more
efficient.

Some examples:

  - `"0,0x3c,128,32"` (small display on bus 0)
  - `"1,0x3d,128,64"` (large display on bus 1 with alternate address)
  - `"*,0x3c,128,64"` (large display, probe busses)

`OLED_TIME` is the minimal on-time of the display. Only relevant in
strobe mode (which will cut power).

On the larger 128x64 display, there is room to display two additional
sensor values in addition to basic status information. The format is

    OLED_VALUES = "sensor1(label1) sensor2(label2)"

The sensor is the same as in `SENSORS`, the label is the same as
during display on a normal (e-ink) screen.

The default is:

    OLED_VALUES = "aht20(T/AHT:) aht20(H/AHT:)"


send_udp
--------

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| UDP_IP                      | IP   |  M  | IP address of destination |
| UDP_PORT                    | int  |  M  | port of destination       |

As network related configurations, these two values have to be
configured in [`secrets.py`](./secrets.md).
