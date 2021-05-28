#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

import dbus.service

from echoez.config import *
from echoez.err import *
from echoez.characteristic import (
    EchoCharacteristic,
    EchoEncryptCharacteristic,
    EchoSecureCharacteristic,
)

__all__ = [
    "Service",
]


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation

    Base class for other services
    """

    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": dbus.Array(
                    self.get_characteristic_paths(), signature="o"
                ),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class EchoService(Service):
    """
    Dummy test service that provides characteristics and descriptors that
    exercise various API functionality.

    """

    ECHO_SVC_UUID = "8e89af16-c001-11eb-aa4c-c3c6adc0b74b"

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.ECHO_SVC_UUID, True)
        self.add_characteristic(EchoCharacteristic(bus, 0, self))
        self.add_characteristic(EchoEncryptCharacteristic(bus, 1, self))
        self.add_characteristic(EchoSecureCharacteristic(bus, 2, self))
