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
        <param field="Mode1" label="Devices" width="300px">
            <description>List of IP addresses to check (comma separated)</description>
        </param>
        <param field="Mode2" label="Ping interval" width="75px" default="10">
            <description>Interval between checks in seconds (in the range [5, 60])</description>
        </param>
        <param field="Mode3" label="Cooldown" width="75px" default="60">
            <description>Time before updating Domoticz device status when a device goes offline</description>
        </param>
        <param field="Mode4" label="Ping tool" width="100px">
          <description>Ping tool to use, default to standard ping. Some devices (smartphones) may not reply to ping and detection may be unreliable (when a smartphone is idle it may not always reply to echo requests).<br/>
          Arping is more reliable but requires to use sudo. If arping is selected, local user running domoticz needs to be able to run arping through sudo without password.<br/>
          This can be done by adding in the sudoers file:<br/>
          username ALL=(ALL) NOPASSWD:/sbin/arping</description>
          <options>
            <option label="ping (default)" value="ping" default="true"/>
            <option label="arping" value="arping"/>
          </options>
        </param>
        <param field="Mode6" label="Debug" width="100px">
          <options>
            <option label="True" value="Debug"/>
            <option label="False (default)" value="Normal" default="true"/>
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
        self.use_arping = False

    def onStart(self):
        self.devices = Parameters['Mode1'].split(',')

        if Parameters['Mode6'] == 'Debug':
            Domoticz.Debugging(1)

        # types / subtypes reference: https://github.com/domoticz/domoticz/blob/master/hardware/hardwaretypes.h
        unit = 1
        for dev in self.devices:
            if (unit not in Devices):
                Domoticz.Device(Name='Device '+dev, Unit=unit, TypeName='Switch', Used=1).Create()
            unit += 1

        if Parameters['Mode4'] == 'arping':
            self.use_arping = True

        itvl = 10
        if Parameters['Mode2'] != '':
            itvl = int(Parameters['Mode2'])
        itvl = max(5, min(itvl, 60))

        Domoticz.Heartbeat(itvl)

    def pingDevice(self, ip):
        if self.use_arping == False:
            cmd = ['/usr/bin/ping', '-q', '-c1', '-W', '1', ip]
        else:
            cmd = ['/usr/bin/sudo', '/sbin/arping', '-q', '-c1', '-W', '1', ip]
        Domoticz.Debug('Ping command: {:s}'.format(' '.join(cmd)))
        ping_reply = subprocess.run(cmd, capture_output = True, shell = False)
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
                    Domoticz.Log(ip + ' came back online, no need to update device {:d}'.format(idx))
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
