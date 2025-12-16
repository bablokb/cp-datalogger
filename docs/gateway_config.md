Gateway Configuration
=====================

A number of specifc configuration constants are necessary to operate
the gateway.  Copy the file `src.gateway/config_template.py` and adapt
the config-variables for your setup.

Note that for the optional hardware-components RTC, SD and
OLED-display you have to add the relevant configuration as described
in [main configuration](./core_config_main.md).

The configuration of the log-writer is identical to the way this is
implemented for the dataloggers. I.e. you should copy the file
`src/log_config_template.py` and choose the logger you need. See [Log
configuration](./log_config.md) for details.


Gateway-Identification
-----------------------

| Name          | Type | O/M | Description                 |
|---------------|------|-----|-----------------------------|
| GW_NAME       | str  |  M  | Name of the gateway (unused)|
| GW_ID         | str  |  M  | ID of the gateway           |
| GW_LOCATION   | str  |  M  | Location (unused)           |
| GW_TITLE      | str  |  O  | Title (unused)              |

The `GW_ID` can be used as placeholder in the `CSV_FILENAME`.


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


Tasks
-----

| Name                | Type | O/M | Description                  |
|---------------------|------|-----|------------------------------|
| TASKS               | str  |  M  | List of post-data tasks      |
| BTASKS              | str  |  M  | List of post-broadcast tasks |

List of tasks to execute. This is a blank delimited list. See
[tasks](./gateway_tasks.md) for a list of available tasks and also check
[task-specific configuration](./gateway_config_tasks.md).

Tasks can be used to send data from the gateway to upstream or to
save data to a SD-card.

Tasks listed in `BTASKS` are for development and troubleshooting only
and should normally be not necessary.


LoraReceiver
------------

| Name                    | Type | O/M | Description                           |
|-------------------------|------|-----|---------------------------------------|
| LORA_FREQ               | float|  M  | 433 / 868 / 915                       |
| LORA_NODE_ADDR          | int  |  M  | node-address (usually 0)              |
| LORA_QOS                | int  |  O  | quality of service (0-7)              |
| LORA_TX_POWER           | int  |  O  | transmit power (5-23)                 |
| LORA_GW_RECEIVE_TIMEOUT | float|  O  | LoRa receive timeout (1.0)            |

**Note**: from the gateway perspective, the gateway is the "node", so
the `LORA_NODE_ADDR` has to be configured and not the `LORA_BASE_ADDR`!!

Quality of service ranges from 0 (fastest) to 7 (most robust). Default
value is 2. See [LoRa Setup](./lora.md) for details. **The QoS-parameter
must be identical for dataloggers and the gateway!**


BluesSender
-----------

| Name                   | Type | O/M | Description                           |
|------------------------|------|-----|---------------------------------------|
| BLUES_SYNC_ACTION      | bool |  M  | see below                             |
| BLUES_MAX_SYNC_TIME    | int  |  O  | wait for time-sync on cold-boot (300) |
| BLUES_GET_TIME_RETRIES | int  |  O  | get time retries (3)                  |

`BLUES_SYNC_ACTION` configures the action to perform when receiving data:

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
| UDP_HOST            | str  |  M  | Host or IP-address of UDP-receiver    |
| UDP_PORT            | int  |  M  | Port of UDP-receiver                  |


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
