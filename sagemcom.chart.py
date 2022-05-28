# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Put your name here (your github login)
# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio

from sagemcom_api.enums import EncryptionMethod
from sagemcom_api.client import SagemcomClient

from bases.FrameworkServices.SimpleService import SimpleService

RX = 'optical_rx'
TX = 'optical_tx'
CPU = 'cpu_usage'
DATA = 'data_usage'

ORDER = [
    RX,
    TX,
    CPU,
    DATA
]

CHARTS = {
    RX: {
        'options': [None, 'GPON - RX', 'dbm', 'GPON', 'GPON', 'line'],
        'lines': [
            [RX, 'Optical Module Rx Power', 'absolute', 1, 1000],
        ]
    },
    TX: {
        'options': [None, 'GPON - TX', 'dbm', 'GPON', 'GPON', 'line'],
        'lines': [
            [TX, 'Optical Module Tx Power', 'absolute', 1, 1000]
        ]
    },
    CPU: {
        'options': [None, 'CPU Usage', 'percentage', 'CPU', 'CPU', 'area'],
        'lines': [
            [CPU, 'Total CPU', 'absolute', 1, 1]
        ]
    },
    DATA: {
        'options': [None, 'WAN Data Usage', 'MB', 'Data Usage', 'Data', 'area'],
        'lines': [
            ['received', 'Received', 'incremental', 1, 1024 * 1024],
            ['sent', 'Sent', 'incremental', -1, 1024 * 1024]
        ]
    }

}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.HOST = self.configuration.get('HOST', "ERROR")
        self.USERNAME = self.configuration.get('USERNAME', "ERROR")
        self.PASSWORD = self.configuration.get('PASSWORD', "ERROR")
        self.ENCRYPTION_METHOD = EncryptionMethod.MD5
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

    async def poll_sagemcom(self):
        data = dict()

        async with SagemcomClient(self.HOST, self.USERNAME, self.PASSWORD, self.ENCRYPTION_METHOD) as client:
            self.debug("Starting sagemcom client ")
            try:
                await client.login()
            except Exception as exception:  # pylint: disable=broad-except
                data[RX] = 0
                data[TX] = 0
                self.error(exception)
                return data

            if not self.name_captured:
                # Print device information of Sagemcom F@st router
                device_info = await client.get_device_info()
                self.debug(f"Old name: {CHARTS[RX]['options'][3]}")
                self.debug(f"{device_info.id} {device_info.model_name}")
                self.charts[RX].update(self, dict(family=device_info.model_name))
                self.charts[TX].update(self, dict(family=device_info.model_name))
                self.name_captured = True

            # # Print connected devices
            # devices = await client.get_hosts()
            #
            # for device in devices:
            #     if device.active:
            #         print(f"{device.id} - {device.name}")

            # # Retrieve values via XPath notation, output is a dict
            # custom_command_output = await client.get_value_by_xpath("Device/UserInterface/AdvancedMode")
            # print(custom_command_output)

            optical_signal_level = int(
                await client.get_value_by_xpath("Device/Optical/Interfaces/Interface[@uid='1']/OpticalSignalLevel"))
            self.debug(optical_signal_level)
            data[RX] = optical_signal_level

            transmit_optical_level = int(
                await client.get_value_by_xpath("Device/Optical/Interfaces/Interface[@uid='1']/TransmitOpticalLevel"))
            self.debug(transmit_optical_level)
            data[TX] = transmit_optical_level

            cpu_usage = await client.get_value_by_xpath("Device/DeviceInfo/ProcessStatus/CPUUsage")
            self.debug(cpu_usage)
            data[CPU] = cpu_usage

            data_usage = await client.get_value_by_xpath("Device/IP/Interfaces/Interface[@uid='2']/Stats")
            data['received'] = data_usage['stats']['bytes_received']
            data['sent'] = data_usage['stats']['bytes_sent']
            self.debug(data_usage['stats'])

            await client.close()
            # Set value via XPath notation
            # custom_command_output = await client.set_value_by_xpath("Device/UserInterface/AdvancedMode", "true")
            # print(custom_command_output)

            return data

    def get_data(self):
        self.debug("get_data")
        return self.run_async([self.poll_sagemcom()])
