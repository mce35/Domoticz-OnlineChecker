# Domoticz-OnlineChecker-Plugin

A simple Domoticz Python plugin to check whether devices are online, based on ping.

This can be used to detect mobile phones to do some kind of geofencing.

The plugin is originally based on script described [here](https://www.domoticz.com/wiki/Presence_detection)

## Plugin Parameters

| Field         | Description |
|---------------|-------------|
| Devices       | List of devices to check, can be IP addresses or hostnames |
| Ping interval | Interval between pings, in seconds |
| Cooldown      | Time to wait when the device goes offline before actually changing the Domoticz device status, in seconds |

## How to use

After adding the plugin, it will create one switch device per IP address configuredin the list.

Each switch will reflect the device reachability:

- `0` or `Off`: Device is not reachable using `ping`
- `1` or `On`: Device is reachable using `ping`

## TODO

- Allow to use `arping` (with `sudo`)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?business=VNKNGYUAZQR6A&no_recurring=0&currency_code=EUR)
