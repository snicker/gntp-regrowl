# ReGrowl Server

Forked by snicker in Sept 2013 to act as a headless GNTP server to bouncing messages to other clients. Will eventually support:

* Forwarding to multiple machines
* Forwarding based in incoming messages host address, application name, message type, etc
* Web GUI for modifying forwarding configuration data

Currently supports:

* Forwarding all messages to a single machine

Completely based on the work done by KFDM, one of the only GNTP solutions I've seen that works on FreeBSD.

## Installing

	python setup.py install
	
## Running
```
$ regrowl -h
Usage: regrowl [options]

Options:
  -h, --help            show this help message and exit
  -a HOST, --address=HOST
                        address to listen on
  -p PORT, --port=PORT  port to listen on
  -P PASSWORD, --password=PASSWORD
                        Network password
  -v, --verbose         
```

## Config File

Regrowl bridges can be controled through a simple config file in `~/.regrowl`

```
[regrowl.server]
port = 12345
password = mypassword

[regrowl.bridge.local]
enabled = false

[regrowl.bridge.subscribe]
enabled = false
```

Config file sections are defined by the package name.

## See Also

* [Python GNTP Library](https://github.com/kfdm/gntp) Used to decode incoming growl messages
