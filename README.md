EyeFiLinuxUi
------------

Guess what! This is a VERY simple UI to use EyeFi cards on Linux.

What does?
----------

When starts:

- disconnect wifi interfaz (using `nmcli`)
- launches hostapd (using `kdesudo` + `hostapd`)
- launches dhcpd (using the `udhcpd` applet of `busybox`)
- setup interface and firewall (using `kdesudo` + `iptables` + `ifconfig`)
- launches EyeFiServer2 (a slightly modified version of [EyeFiServer2](https://code.google.com/p/eyefiserver2/))

And then:

- on each upload, the image is shown in the UI, and a thumbnail is added, this is glued together using `RabbitMQ`.

Requires
--------

- Python + Qt (PySide)
- kdesudo (to setup network, firewall and start services)
- BusyBox (udhcpd)
- HostAPd
- RabbitMQ
- a wireless interface

This is currently developed and tested on Ubuntu 12.10.

Notes
-----

- the wireless interface is turned down using nmcli. To give it back to life, use `nmcli con up id NETWORKNAME`.

License
-------

GPLv3. See `LICENSE.txt`.

Includes the code from [EyeFiServer2](https://code.google.com/p/eyefiserver2/) which is also GPLv3
