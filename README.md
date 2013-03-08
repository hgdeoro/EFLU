EFLU
------------

This is a VERY simple UI to receive images from a EyeFi cards on Linux. I use it to upload the photos from the camera to the computer, ensuring the EyeFi card is *NOT* connected to internet.

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

Example
-------

    ./main.sh --interface wlan0 --wifi_ssid MY-PRIVATE-WIFI-NETWORK --wifi_passphrase WIFI-PASSWORD \
        --eyefi_upload_key 0123456789abcdef0123456789abcdef --eyefi_mac XX:XX:XX:XX:XX:XX \
        --upload_dir /path/to/directory


Requires
--------

- Python + Qt (PySide)
- kdesudo (to setup network, firewall and start services)
- BusyBox (udhcpd)
- HostAPd
- RabbitMQ
- a wireless interface

This is currently developed and tested on Ubuntu 12.10. You need at least: `hostapd`, `busybox-static`, `rabbitmq-server`, `kdesudo`, `python-pyside`.

Screenshot
----------

![EFLU Screenshot](https://raw.github.com/hgdeoro/EFLU/master/eflu-screenshot-2.jpg "Screenshot")


Notes
-----

- the wireless interface is turned down using nmcli. To give it back to life, use `nmcli con up id NETWORKNAME`.

License
-------

GPLv3. See `LICENSE.txt`.

Includes the code from [EyeFiServer2](https://code.google.com/p/eyefiserver2/) which is also GPLv3.

All trademarks belong to legitimate owners.
