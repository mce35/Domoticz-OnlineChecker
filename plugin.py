# ArduinoIO Python plugin for Domoticz
#
#
"""
<plugin key="online-checker" name="OnlineChecker" author="mce35" version="0.1.0">
    <description>
        <h1>Plugin for checking device status, based on ping command. The ping command must be available in /usr/bin/ping</h1><br/>
        <h2>Parameters</h2>
    </description>
    <params>
        <param field="Mode1" label="Devices" width="150px">
            <description>List of IP addresses to check (comma separated)</description>
        </param>
        <param field="Mode2" label="Ping interval" width="75px" default="10">
            <description>Interval between checks in seconds</description>
        </param>
        <param field="Mode3" label="Cooldown" width="75px" default="60">
            <description>Time before updating Domoticz device status when a device goes offline</description>
        </param>
        <param field="Mode6" label="Debug" width="75px">
          <options>
            <option label="True" value="Debug"/>
            <option label="False (default)" value="Normal" default="true" />
          </options>
        </param>
    </params>
</plugin>
"""
import datetime
import subprocess
import Domoticz

class BasePlugin:
    def __init__(self):
        self.last_seen = {}
        self.was_online = {}
        self.last_reported = {}

    def onStart(self):
        Domoticz.Log('Starting plugin')
        self.devices = Parameters['Mode1'].split(',')

        if Parameters['Mode6'] == 'Debug':
            Domoticz.Debugging(1)

        # types / subtypes reference: https://github.com/domoticz/domoticz/blob/master/hardware/hardwaretypes.h
        unit = 1
        for dev in self.devices:
            if (unit not in Devices):
                Domoticz.Device(Name='Device '+dev, Unit=unit, TypeName='Switch', Used=1).Create()
            unit += 1

        itvl = 10
        if Parameters['Mode2'] != '':
            itvl = int(Parameters['Mode2'])
        itvl = max(5, min(itvl, 60))

        Domoticz.Heartbeat(itvl)

    def pingDevice(self, ip):
        cmd = ['/usr/bin/ping', '-q', '-c1', '-W', '1', ip]
        Domoticz.Debug('Ping command: {:s}'.format(' '.join(cmd)))
        ping_reply = subprocess.run(cmd, capture_output = False, shell = False, timeout = 5)
        return bool(ping_reply.returncode == 0)

    def timeout(self, last_seen):
        return (datetime.datetime.now() - last_seen).total_seconds() > int(Parameters['Mode3'])

    def checkDevice(self, ip, idx):
        is_online = self.pingDevice(ip)

        if not ip in self.last_seen:
            self.last_seen[ip] = datetime.datetime.now()
            self.was_online[ip] = None
            self.last_reported[ip] = None

        if is_online:
            self.last_seen[ip] = datetime.datetime.now()
            if is_online != self.was_online[ip]:
                if self.last_reported[ip]:
                    Domoticz.Log(ip + ' came back online, no need to tell Domoticz.')
                else:
                    Domoticz.Log(ip + ' came online, updating device {:d}'.format(idx))
                    if idx in Devices:
                        Devices[idx].Update(1, 'On')
                    self.last_reported[ip] = True
        else:
            if is_online != self.was_online[ip]:
                Domoticz.Log(ip+' went offline, waiting for it to come back...')
            if self.timeout(self.last_seen[ip]) and (self.last_reported[ip] or self.last_reported[ip] == None):
                if idx in Devices:
                    Devices[idx].Update(0, 'Off')
                Domoticz.Log(ip+' went offline, updating device {:d}'.format(idx))
                self.last_reported[ip] = False

        self.was_online[ip] = is_online


    def onStop(self):
        Domoticz.Debug('onStop called')

    def onHeartbeat(self):
        Domoticz.Debug('onHeartbeat called')
        unit = 1
        for dev in self.devices:
            self.checkDevice(dev, unit)
            unit += 1

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
