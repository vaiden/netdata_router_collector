# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Put your name here (your github login)
# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio

from sagemcom_api.enums import EncryptionMethod
from sagemcom_api.client import SagemcomClient

from bases.FrameworkServices.SimpleService import SimpleService

RX = 'o'
TX = 't'

ORDER = [
    'rxtx',
]

CHARTS = {
    'rxtx': {
        'options': [None, 'GPON', 'dbm', 'GPON', 'GPON', 'line'],
        'lines': [
            [RX, 'Optical Module Rx Power'],
            [TX, 'Optical Module Tx Power']
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
                self.debug(exception)
                return data

            # Print device information of Sagemcom F@st router
            device_info = await client.get_device_info()
            self.debug(f"{device_info.id} {device_info.model_name}")

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

            await client.close()
            # Set value via XPath notation
            # custom_command_output = await client.set_value_by_xpath("Device/UserInterface/AdvancedMode", "true")
            # print(custom_command_output)

            return data

    def get_data(self):
        self.debug("get_data")
        return self.run_async([self.poll_sagemcom()])
