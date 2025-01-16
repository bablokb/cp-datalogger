Gateway Configuration
=====================

A number of specifc configuration constants are necessary to operate
the gateway.  Copy the file `src.gateway/config_template.py` and adapt
the config-variables for your setup.

Note that for the optional hardware-components RTC, SD and
OLED-display you have to add the relevant configuration as described
in [main configuration](./core_config_main.md). **The normal defaults
are not valid for a gateway, so you must usually add these lines to
your configuration**:

    HAVE_RTC  = None
    HAVE_SD   = None

The configuration of the logger is identical to the way this is
implemented for the data-loggers. I.e. you should copy the file
`src/log_config_template.py` and choose the logger you need. See [Log
configuration](./log_config.md) for details.


Application
-----------

| Name                | Type | O/M | Description                              |
|---------------------|------|-----|------------------------------------------|
| TIME_TABLE          |      |  M  | time-table                               |
| ON_DURATION         | int  |  M  | on-duration in minutes                   |
| GW_RX_TYPE          | str  |  O  | 'Noop', 'Lora', 'UDP'¹, 'BLE'¹ ('Lora')  |
| GW_TX_TYPE          | str  |  O  | 'Noop', 'Blues', 'UDP', 'BLE'¹ ('Blues') |

¹not implemented yet

For details about `TIME_TABLE` see [main configuration](./core_config_main.md).


LoraReceiver
------------

| Name                | Type | O/M | Description                           |
|---------------------|------|-----|---------------------------------------|
| RECEIVE_TIMEOUT     | float|  O  | LoRa receive timeout (1.0)            |
| LORA_FREQ           | float|  M  | 433 / 868 / 915                       |
| LORA_NODE_ADDR      | int  |  M  | node-address (usually 0)              |
| LORA_ENABLE_TIME    | float|  O  | enable wait-time (0)                  |
| LORA_ACK_WAIT       | float|  O  | wait for ACK time (0.25)              |
| LORA_ACK_RETRIES    | int  |  O  | send retries (3)                      |
| LORA_TX_POWER       | int  |  O  | transmit power (5-23)                 |

**Note**: from the gateway perspective, the gateway is the "node", so
the `LORA_NODE_ADDR` has to be configured and not the `LORA_BASE_ADDR`!!


BluesSender
-----------

| Name                | Type | O/M | Description                           |
|---------------------|------|-----|---------------------------------------|
| SYNC_BLUES_ACTION   | bool |  M  | see below                             |
| MAX_SYNC_TIME       | int  |  O  | wait for time-sync on cold-boot (300) |


`SYNC_BLUES_ACTION` configures the action to perform when receiving data:

  - None:  no action, just print to log
  - False: buffer data to notecard, sync after active window
  - True:  don't buffer data, sync to Notehub immediately

On cold boot, the notecard will synchronize it's time with the
WAN-network.  The duration depends on various technical
parameters. The wait time has to be configured accordingly. Usually,
something like 120s is normal, so the default will be fine.


UDPSender
---------

| Name                | Type | O/M | Description                           |
|---------------------|------|-----|---------------------------------------|
| TX_UDP_HOST         | str  |  M  | Host or IP-address of UDP-receiver    |
| TX_UDP_PORT         | int  |  M  | Port of UDP-receiver                  |


See [datalogger receiver service](../src.receiver_service/Readme.md) for
a simple implementation of a central receiver.


Development Settings
--------------------

| Name              | Type | O/M | Description                       |
|-------------------|------|-----|-----------------------------------|
| DEV_MODE          | bool |  O  | Development mode (default: False) |

Development-mode and other (future) development settings allow to test
the program behavior. Settings starting with `DEV_` should not be
changed unless you are a software-developer and understand the
implications.
