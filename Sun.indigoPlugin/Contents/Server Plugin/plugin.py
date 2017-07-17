#!/usr/bin/env python
# coding: utf-8

import ephem
import indigo
import math

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion,
                 pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        self.debug = pluginPrefs.get('debug', False)

        self.devices = {}

    def deviceStartComm(self, device):
        if device.id not in self.devices:
            self.devices[device.id] = device

    def deviceStopCom(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def update(self, body):
        self.debugLog('Updating body %s' % body.id)

        sun = ephem.Sun()
        sun.compute(self.observer())

        self.debugLog('alt: %s az: %s' % (sun.alt, sun.az))

        body.updateStateOnServer('altitude', math.degrees(sun.alt))
        body.updateStateOnServer('azimuth',  math.degrees(sun.az))

    def updateAll(self):
        for _, sun in self.devices.iteritems():
            self.update(sun)

    def observer(self):
        observer = ephem.Observer()

        latitude, longitude = indigo.server.getLatitudeAndLongitude()

        observer.lat = str(latitude)
        observer.lon = str(longitude)

        return observer

    def runConcurrentThread(self):
        while True:
            if len(self.devices) > 0:
                self.updateAll()

                # pick a random sun for the update interval
                sun = self.devices[self.devices.keys()[0]]

                interval = float(sun.pluginProps['updateInterval']) * 60
            else:
                interval = 240

            self.sleep(interval)
