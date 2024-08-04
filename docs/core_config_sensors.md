Sensor Specific Configuration
=============================

Most [sensors](./sensors.md) will will not need any specific configuration.
There are a few exceptions.

Some sensors will report multiple properties, e.g. temperature,
humidity and pressure. The value of `xxxx_PROPERTIES` will configure
which of them (and in which order) are shown on the display. Note that
all values will be recorded in the CSV regardless of the value of
`xxxx_PROPERTIES`. it is also possible to exclude all sensor
properties from the display by adding them to `SENSORS_CSV_ONLY`.


AHT20
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| AHT20_PROPERTIES            | str  |  O  | properties for display    |
|                             |      |     | ("t h")                   |


AM2320
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| AM2320_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t h")                   |


BME280
------

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| BMx280_ALTITUDE_AT_LOCATION | int  |  O  | altitude in meters (525)  |
| BME280_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t h ps")                |

The altitude is necessary to convert pressure readings to sea-level
pressure. Default is 525m.


BMP280
------

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| BMx280_ALTITUDE_AT_LOCATION | int  |  O  | altitude in meters (525)  |
| BMP280_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t ps")                  |

The altitude is necessary to convert pressure readings to sea-level
pressure. Default is 525m.


ENS160
------

| Name              | Type | O/M | Description                              |
|-------------------|------|-----|------------------------------------------|
| ENS160_DISCARD    | bool |  O  | only keep last readout (True)            |
| ENS160_INTERVALS  | list |  O  | list of sampling intervals ([0,5])       |
| ENS160_WARMUP     | int  |  O  | wait-time when status==1 (190)           |
| ENS160_PROPERTIES | str  |  O  | properties for display ("AQI TVOC eCO2") |

The ENS160 gives better results with multiple samples. Normally, only the
last sample is saved to CSV, the others are discarded. For testing purposes,
this behaviour can be change with `ENS160_DISCARD`.

`ENS160_INTERVALS` will define the number of samples as well as the
intervals between samples. The default samples once at readout time and
then again five seconds later.

In case the sensor is in it's initial startup-phase (`status==2`), all values
returned will be zero. When `status==1` (warmup), the system switches
to deep-sleep for `ENS160_WARMUP` seconds.

The sensor queries three properties: an "air quality index", the
"total volatile organic compounds" and "equivalent CO2". Since the values
of the AQI seem useless and the TVOC and eCO2 are highly correlated,
only a subset of the properties can be displayed on the display. The
CSV will always record all properties (including status).


HTU31D
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| HTU31D_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t h")                   |


Open-Meteo
----------

| Name              | Type | O/M | Description                          |
|-------------------|------|-----|--------------------------------------|
| METEO_LATITUDE    |float |  O  | Default: 48.6967                     |
| METEO_LONGITUDE   |float |  O  | Default: 13.4631                     |
| METEO_PROPERTIES  | str  |  O  | properties for display               |
|                   |      |     | ("t h ps code w_speed w_dir r")      |


Data provided by <https://open-meteo.com> ("current weather").
Note that the default latitude/longitude are just somewhere, so
these values are technically optional, but should be treated as
mandatory nevertheless.


PMS5003
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| PMS5003_PROPERTIES          | str  |  O  | properties for display    |
|                             |      |     | ("p03 p10 p25")           |


SCD40, SCD41
------------

| Name              | Type | O/M | Description                        |
|-------------------|------|-----|------------------------------------|
| SCD4X_SAMPLES     | int  |  O  | number of samples (2)              |
| SCD4X_TIMEOUT     | int  |  O  | timeout waiting for data (10)      |
| SCD4X_DISCARD     | bool |  O  | only keep last readout (True)      |
| SCD4X_PROPERTIES  | str  |  O  | properties for display ("c t h")   |

The SCD4x-sensors give better results with multiple samples. Normally,
only the last sample is saved to CSV, the others are discarded. For
testing purposes, this behaviour can be change with `SCD4X_DISCARD`.

Periodic measurement on SCD4x should return data every five seconds.
After `SDC4X_TIMEOUT` seconds the sensor-wrapper will give up. The
default should be ok.


SHT45
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| SHT45_PROPERTIES            | str  |  O  | properties for display    |
|                             |      |     | ("t h")                   |
