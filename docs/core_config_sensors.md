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
| ALTITUDE_AT_LOCATION        | int  |  O  | altitude in meters (540)  |
| BME280_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t h pl ps")             |

Properties:

  - t: temperature
  - h: humidity
  - pl: pressure at location
  - ps: pressure at sea-level (converted)

The altitude is necessary to convert pressure readings to sea-level
pressure. Default is 540m.


BMP280
------

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| ALTITUDE_AT_LOCATION        | int  |  O  | altitude in meters (540)  |
| BMP280_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t pl ps")               |

Properties:

  - t: temperature
  - pl: pressure at location
  - ps: pressure at sea-level (converted)

The altitude is necessary to convert pressure readings to sea-level
pressure. Default is 540m.


ENS160
------

| Name              | Type | O/M | Description                              |
|-------------------|------|-----|------------------------------------------|
| ENS160_DISCARD    | bool |  O  | only keep last readout (True)            |
| ENS160_INTERVALS  | list |  O  | list of sampling intervals ([0,5])       |
| ENS160_WARMUP     | int  |  O  | wait-time when status==1 (190)           |
| ENS160_PROPERTIES | str  |  O  | properties for display ("AQI TVOC eCO2") |

The ENS160 gives better results with multiple samples. Normally, only
the last sample is saved to CSV, the others are discarded. For testing
purposes, this behaviour can be change with `ENS160_DISCARD`.

`ENS160_INTERVALS` will define the number of samples as well as the
intervals between samples. The default samples once at readout time
and then again five seconds later.

In case the sensor is in it's initial startup-phase (`status==2`), all
values returned will be zero. When `status==1` (warmup), the system
switches to deep-sleep for `ENS160_WARMUP` seconds.

The sensor queries three properties: an "air quality index", the
"total volatile organic compounds" and "equivalent CO2". Since the
values of the AQI seem useless and the TVOC and eCO2 are highly
correlated, only a subset of the properties can be displayed on the
display using `ENS160_PROPERTIES`. The CSV will always record all
properties (including status).


HTU31D
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| HTU31D_PROPERTIES           | str  |  O  | properties for display    |
|                             |      |     | ("t h")                   |


MHZ19
-------

| Name                   | Type | O/M | Description                    |
|------------------------|------|-----|--------------------------------|
| MHZ19_RETRIES          | int  |  O  | retry reads (3)                |
| MHZ19_PROPERTIES       | str  |  O  | properties for display ("c t") |
| MHZ19_INIT_TIME        | int  |  0  | initialization time (60)       |
| MHZ19_AUTO_CALIB       | bool |  0  | set auto-calibration (False)   |


Open-Meteo
----------

| Name              | Type | O/M | Description                         |
|-------------------|------|-----|-------------------------------------|
| METEO_LATITUDE    |float |  O  | Default: 48.6967                    |
| METEO_LONGITUDE   |float |  O  | Default: 13.4631                    |
| METEO_PROPERTIES  | str  |  O  | properties for display              |
|                   |      |     | ("t h ps code w_speed w_dir r")     |


Data provided by <https://open-meteo.com> ("current weather").
Note that the default latitude/longitude are just somewhere, so
these values are technically optional, but should be treated as
mandatory nevertheless.


PMS5003
-------

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| PMS5003_RETRIES             | int  |  O  | retry reads (3)           |
| PMS5003_PROPERTIES          | str  |  O  | properties for display    |
|                             |      |     | ("p03 p10 p25")           |
| PMS5003_PN_FACTOR           | float|  O  | factor for particle count |
|                             |      |     | (0.01)                    |

Available properties:

  - `pm<x>`: mass concentration of particles, measured in µg/m³ 
     x = 10, 25, 100 (pm10: mass concentration PM1.0 etc.)
  - `pn<x>`: number concentration of particles measured in particles/cm³ 
     x = 03, 05, 10, 25, 50, 100

The default value of `PMS5003_PN_FACTOR` converts the raw count per
0.1L to particles per cm³.

Note that particles larger than 2.5µm are *estimated* and not
measured.  The device will therefore not necessarely detect the
correct concentrations of certain pollutants, e.g. pollen or heavy
dust.


SCD40, SCD41
------------

| Name              | Type | O/M | Description                        |
|-------------------|------|-----|------------------------------------|
| SCD4X_SAMPLES     | int  |  O  | number of samples (2)              |
| SCD4X_INTERVAL    | int  |  O  | sampling-interval (5)              |
| SCD4X_TIMEOUT     | int  |  O  | timeout waiting for data (10)      |
| SCD4X_DISCARD     | bool |  O  | only keep last readout (True)      |
| SCD4X_PROPERTIES  | str  |  O  | properties for display ("c t h")   |

The SCD4x-sensors give better results with multiple samples. Normally,
only the last sample is saved to CSV, the others are discarded. For
testing purposes, this behaviour can be change with `SCD4X_DISCARD`.

Periodic measurement on SCD4x should return data every five seconds.
After `SCD4X_TIMEOUT` seconds the sensor-wrapper will give up. The
default should be ok.

If a measurement from a BME280 or BMP280 is available, the pressure
value is used to configure the ambient pressure of the SCD4x. The
sensors within the `SENSORS`-configuration variable should therefore
be ordered correctly, i.e. first the BMx280, then the SCD4x.


SEN6X
-----

| Name                 | Type | O/M | Description                      |
|----------------------|------|-----|----------------------------------|
| SEN6X_SAMPLES        | int  |  O  | number of samples (2)            |
| SEN6X_INTERVAL       | int  |  O  | sampling-interval (5)            |
| SEN6X_TIMEOUT        | int  |  O  | timeout waiting for data (5)     |
| SEN6X_DISCARD        | bool |  O  | only keep last readout (True)    |
| SEN6X_PROPERTIES     | str  |  O  | properties for display (c t h)   |
| SEN6X_AUTO_CALIBRATE | bool |  O  | auto-calibrate CO2 (False)       |
| SEN6X_TEMP_OFFSET    | [f,f]|  O  | offset and slope (see datasheet) |
| ALTITUDE_AT_LOCATION | int  |  O  | altitude in meters (540)         |

Sensirion's SEN6x sensors are a family of compound sensors for
temperature, humidity, particle and various gases. Currently, the
SEN66 is the only available and supported sensor.

Available properties:

  - `t`: temperature
  - `h`: humidity
  - `c`: CO2
  - `voc`: volatile organic compount index
  - `nox`: NO index
  - `pm<x>`: mass concentration of particles, measured in µg/m³ 
     x = 10, 25, 40, 100 (pm10: mass concentration PM1.0 etc.)
  - `pn<x>`: number concentration of particles measured in particles/cm³ 
     x = 10, 25, 40, 100

The Sen6x-sensors give better results with multiple samples. Normally,
only the last sample is saved to CSV, the others are discarded. For
testing purposes, this behaviour can be change with `SEN6X_DISCARD`.

Periodic measurements on Sen6x should return data every second.
After `SEN6X_TIMEOUT` seconds the sensor-wrapper will give up. The
default should be ok.

If a measurement from a BME280 or BMP280 is available, the pressure
value is used to configure the ambient pressure of the Sen6x. The
sensors within the `SENSORS`-configuration variable should therefore
be ordered correctly, i.e. first the BMx280, then the Sen6x.


SHT45
-----

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| SHT45_PROPERTIES            | str  |  O  | properties for display    |
|                             |      |     | ("t h")                   |


TM_POWER
--------

| Name                     | Type  | O/M | Description                 |
|--------------------------|-------|-----|-----------------------------|
| TM_POWER_PROPERTIES      | str   |  O  | properties for display      |
|                          |       |     | ("P V C")                   |
| TM_POWER_HOSTS           | list  |  O  | list of hosts or IPs        |
| TM_POWER_URL             | str   |  O  | query URL (see below)       |
| TM_POWER_TIMEOUT         | float |  O  | timeout for get-request (2) |

This sensor reads the status of one or more Tasmota smart (power)
plugs, returning power, voltage and current. Setting
`TM_POWER_PROPERTIES="P"` is recommended, since voltage is more
or less constant and current is `P/V`.

The default query URL is `http://<host_or_ip>/cm?cmnd=status%2010`.
