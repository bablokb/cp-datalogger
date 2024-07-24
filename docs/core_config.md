Core Configuration
==================

Overview
--------

The complete configuration of the datalogger engine is within the file
`src/config.py`. This file is listed in `.gitignore` and not synchronized
with Github. The template file `src/config_template.py` serves as a
starting point for your own `config.py`.

Since the path to `config.py` can be passed to the makefile, it can
be maintained out-of-tree. See [deployment](./deployment.md) for details.

Configuration variables can be divided into a number of realms:

  - **main**: all variables of the datacollection-engine
  - **sensors**: variables specific to individual [sensors](./sensors.md)
  - **tasks**: variables specific to individual [tasks](./tasks.md)
  - **broadcast**: variables specific to the [broadcast mode](./broadcast_mode.md)

Most variables have sensible defaults and can be omitted from
the configuration. But some are mandatory, e.g. the selection of
sensors and tasks.


Variables by Realm
------------------

  - [main](./core_config_main.md)
  - [sensors](./core_config_sensors.md)
  - [tasks](./core_config_tasks.md)
  - [broadcast](./core_config_broadcast.md)
