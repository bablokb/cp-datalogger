Log-Configuration
=================

The file `src/log_config.py` defines the destination of technical
log messages. Various options exist:

  - no output
  - output to the console
  - output to the file `messages.log` on the sd-card
  - output to UART-serial

The last option lets you monitor the system even when running on batteries.

In a stable environment the recommended setting is

    g_logger = Logger(None)

Logging to the console only makes sense during development with an attached
PC/Laptop. Logging to SD-card is ideal for the ex-post analysis of problems,
but consumes more energy.

Copy and adapt the file `src/log_config_template.py` to your needs.

Since the path to `log_config.py` can be passed to the makefile, it can
be maintained out-of-tree. See [deployment](deployment.md) for details.
