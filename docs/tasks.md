Post Datacollection Tasks
=========================

After datacollection, an arbitrary number of tasks can be
executed. This is [configured](./core_config_main.md) with the
variable `TASKS` (a blank delimited list of tasks).

Each task needs a wrapper file in `src/tasks` and must define a
`run()`-method.  To create a new task, use one of the existing files
as a template.

Some tasks have task-specific configuration options. See [task
configuration](./core_config_tasks.md) for details.

Available and planned tasks are listed below.


dump_data
---------

This will write sensor-data either to the log or to the serial console.
Note that this task is not really useful in a productive environment, but
is useful for testing.


save_data
--------- 

This task writes the collected sensor data to the configured CSV-file.


update_display
--------------

Update the main main display with sensor measurement data. This task
should run after "save_data" and "send_lora", since it also displays
the status of SD-card writes and transmissions.


update_oled
-----------

Update an attached OLED-display with basic status information and at most
two lines of measurement-data.

This task will only work for setups without main display. It is a diagnostic
task that allows to temporarily plug in an OLED-I2C display, start the
system and see the status. In normal productive environments running in
strobe mode, the display will only be powered for a short time, but that
should be enough to verify the status.

For systems running in continuous mode, this task can be used to update a
permanently attached OLED.


send_lora
---------

Send collected sensor-data to the LoRa-gateway. The data-format is
the same as the data written to the CSV-file with task "save_data".


send_udp
--------

Same as "send_lora", but send data via UDP to a configured target
host/port.

A sample implementation of an UDP gateway is in `tools/udp_gateway.py`.


send_ble_nus
------------

**Planned, but not implemented**

Same as "send_lora", but send data via BLE Nordic UART service. This
task does not work on devices without BLE support like the Pico-W.


send_mqtt
---------

**Not planned, but PR is welcome**

Same as "send_lora", but send data via MQTT.
