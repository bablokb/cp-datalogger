Sensor Specific Configuration
=============================

Most [sensors](./sensors.md) will will not need any specific configuration.
There are a few exceptions.

BME280, BMP280
--------------

BMx280_ALTITUDE_AT_LOCATION

| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| BMx280_ALTITUDE_AT_LOCATION | int  |  O  | altitude in meters (525)  |

The altitude is necessary to convert pressure readings to sea-level
pressure. Default is 525m.


ENS160
------

| Name              | Type | O/M | Description                              |
|-------------------|------|-----|------------------------------------------|
| ENS160_DISCARD    | bool |  O  | only keep last readout (True)            |
| ENS160_INTERVALS  | list |  O  | list of sampling intervals ([0,5])       |
| ENS160_WARMUP     | int  |  O  | wait-time when status==1 (190)           |
| ENS160_PROPERTIES | str  |  O  | properties for display ("aqi tvoc eco2") |

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

The sensors will report three properties: CO2, temperature and humidity.
The value of `SCD4X_PROPERTIES` configures which of them (and in which
order) are displayed. Note that all values will be recorded in the
CSV regardless of the value of `SCD4X_PROPERTIES`.


Open-Meteo
----------

| Name              | Type | O/M | Description                 |
|-------------------|------|-----|-----------------------------|
| METEO_LATITUDE    |float |  O  | Default: 48.6967            |
| METEO_LONGITUDE   |float |  O  | Default: 13.4631            |
| METEO_PROPERTIES  | str  |  O  | TBD                         |

Data provided by <https://open-meteo.com> ("current weather").
Note that the default latitude/longitude are just somewhere, so
these values are technically optional, but should be treated as
mandatory nevertheless.
