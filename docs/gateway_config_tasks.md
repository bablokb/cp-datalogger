Gateway Tasks Specific Configuration
====================================

This document lists all available gateway tasks and the respective
special configuration variables.


bc_save_data
------------

This tasks is a post-broadcast task and allows the gateway to log broadcast
packets including technical data to a file for later analysis and for
documentation.


| Name                        | Type | O/M | Description                    |
|-----------------------------|------|-----|--------------------------------|
| BCAST_CSV_FILENAME          | str  |  O  | filename for saved data        |

The default value of `BCAST_CSV_FILENAME` is `"/sd/bcast_{GW_ID}_{ID}.csv"`,
so the default creates a distinct file for every datalogger.


bc_send_udp
-----------

A post-broadcast task to log broadcast packets to an UDP-host.


| Name                        | Type | O/M | Description               |
|-----------------------------|------|-----|---------------------------|
| BC_UDP_IP                   | IP   |  M  | IP address of destination |
| BC_UDP_PORT                 | int  |  M  | port of destination       |


bc_update_oled
--------------

This post-broadcast task updates a locally attached oled-display with
technical information about received broadcast packets. Besides the
normal oled-configuration, no special configuration is available.


buffer_data
-----------

This tasks writes data packets to a buffer file (`"/sd/tx_buffer.csv"`)
for later processing, typically during shutdown from other components.


save_data
---------

Write data packets to a CSV-file.

| Name                | Type | O/M | Description                   |
|---------------------|------|-----|-------------------------------|
| CSV_FILENAME        | str  |  O  | CSV filename. Details below.  |
| CSV_FIELDNR_ID      | int  |  O  | field number of logger-id (1) |

For details about `CSV_FILENAME`, see the respective section of
[Main Configuration](./core_config_main.md). In the context of a
gateway, there is an additional placeholder available: `{GW_ID}`.

The task tries to extract the logger-id from the received csv-data
packet using `CS_FIELDNR_ID`. This allows to write a single csv-file
per logger. The default value of `CS_FIELDNR_ID=1` corresponds to
a SENSORS definition on the logger with `SENSORS="id ...."`.


tx_send
-------

Pass data packets to the transmitter plugin for further processing.
Used to send data to upstream destinations.


update_oled
-----------

Update a locally attached oled-display from the received data-packet.

