EyeFiLinuxUi
------------

Guess what! This is a VERY simple UI to use EyeFi cards on Linux.

Requires:

- Python + Qt (PySide)
- kdesudo (to setup network, firewall and start services)
- BusyBox (udhcpd)
- HostAPd
- RabbitMQ
- a wireless interface

This is tested on Ubuntu 12.10.

Notes:

- the wireless interface is turned down using nmcli. To give it back to life, use `nmcli con up id NETWORKNAME`.
