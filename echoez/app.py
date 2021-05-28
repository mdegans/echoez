#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

import logging

import dbus.service

from echoez.config import *
from echoez.service import EchoService

__all__ = [
    "App",
]


logger = logging.getLogger(__name__)


class App(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """

    def __init__(self, bus, name: str):
        if not name.isalpha():
            raise ValueError(f"App name must be alphabetical only. '{name}' is invalid")
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(EchoService(bus, 2))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        logger.debug("GetManagedObjects")

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response
