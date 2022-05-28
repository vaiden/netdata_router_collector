# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Put your name here (your github login)
# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio
import pymiwifi

from bases.FrameworkServices.SimpleService import SimpleService

CPU = 'cpu_usage'
DATA = 'data_usage'
CONNECTED = 'connected_devices'

ORDER = [
    CPU,
    DATA
]

CHARTS = {
    CPU: {
        'options': [None, 'CPU Usage', 'percentage', 'CPU', 'CPU', 'area'],
        'lines': [
            [CPU, 'Total CPU', 'absolute', 1, 100]
        ]
    },
    DATA: {
        'options': [None, 'WAN Data Usage', 'MB', 'Data Usage', 'Data', 'area'],
        'lines': [
            ['received', 'Received', 'incremental', 1, 1024 * 1024],
            ['sent', 'Sent', 'incremental', -1, 1024 * 1024]
        ]
    },
    CONNECTED: {
        'options': [None, 'Connected Devices', 'count', 'Devices', 'Devices', 'line'],
        'lines': [
            [CONNECTED, 'Connected Devices', 'absolute', 1, 1]
        ]
    }

}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.HOST = self.configuration.get('HOST', "ERROR")
        self.PASSWORD = self.configuration.get('PASSWORD', "ERROR")
        self.name_captured = False

    @staticmethod
    def check():
        return True

    def run_async(self, jobs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ret_val = loop.run_until_complete(asyncio.gather(*jobs))[0]
        self.debug("ret_val={ret_val}".format(**vars()))
        loop.close()
        return ret_val

    def poll_xiaomi(self):
        data = dict()

        miwifi = pymiwifi.MiWiFi(f"http://{self.HOST}/")
        miwifi.login('***REMOVED***')
        values = miwifi.status()

        if not self.name_captured:
            # Print device information of Xiaomi MiWifi router
            name = values["hardware"]["platform"]
            mac = values["hardware"]["mac"]
            self.debug(f"{mac} {name}")
            self.name_captured = True

        data[CPU] = values["cpu"]["load"]/values["cpu"]["core"] * 100 * 100
        data['received'] = values["wan"]["download"]
        data['sent'] = values["wan"]["upload"]
        data['connected'] = values["count"]["online"]
        self.debug("ret_val={data}".format(**vars()))
        return data

    def get_data(self):
        self.debug("get_data")
        return self.poll_xiaomi()
