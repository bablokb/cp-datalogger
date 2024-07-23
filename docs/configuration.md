Configuration
=============

The datalogger-software usually does not need extra programming, since
almost everything is configurable. The drawback is a long list of
configuration options. To make things simple, most options have
sensible defaults and don't need to be set explicitly.

Nevertheless, a few things have to be configured. Configuration uses a total
of four files, mainly to separate things and to allow reuse:

  - WLAN credentials: [`secrets.py`](./secrets.md)
  - Log configuration: [`log_config.py`](./log_config.md)
  - Core configuration: [`config.py`](./core_config.md)
  - Access-Point configuration: [`ap_config.py`](./ap_config.md)
  - When running a gateway: [gateway configuration](./gateway_config.md)

All configuration files are listed in `.gitignore` and are *not*
synchronized with Github to protect credentials. Therefore, you can
just add them to the `src/`-directory.

A better solution, especially if you want to maintain multiple
configurations in parallel, is to keep these files out-of-tree and
pass them to the makefile during building. See
[deployment](deployment.md) for details.

Note that the gateway configuration is only necessary if you use
a gateway for central data collection and relaying.
