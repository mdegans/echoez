#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

import array

import dbus.service

from echoez.config import *
from echoez.err import *

__all__ = [
    "Descriptor",
    "EchoDescriptor",
    "EchoEncryptDescriptor",
    "EchoSecureDescriptor",
    "CharacteristicUserDescriptionDescriptor",
]


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """

    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + "/desc" + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_DESC_IFACE: {
                "Characteristic": self.chrc.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        print("Default ReadValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        print("Default WriteValue called, returning error")
        raise NotSupportedException()


class EchoDescriptor(Descriptor):
    """
    Dummy test descriptor. Returns a static value.

    """

    TEST_DESC_UUID = "12345678-1234-5678-1234-56789abcdef2"

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self, bus, index, self.TEST_DESC_UUID, ["read", "write"], characteristic
        )

    def ReadValue(self, options):
        return [dbus.Byte("E"), dbus.Byte("c"), dbus.Byte("h"), dbus.Byte("o")]


class EchoEncryptDescriptor(Descriptor):
    """
    Dummy test descriptor requiring encryption. Returns a static value.

    """

    TEST_DESC_UUID = "12345678-1234-5678-1234-56789abcdef4"

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self,
            bus,
            index,
            self.TEST_DESC_UUID,
            ["encrypt-read", "encrypt-write"],
            characteristic,
        )

    def ReadValue(self, options):
        return [dbus.Byte("E"), dbus.Byte("c"), dbus.Byte("h"), dbus.Byte("o")]


class EchoSecureDescriptor(Descriptor):
    """
    Dummy test descriptor requiring secure connection. Returns a static value.

    """

    TEST_DESC_UUID = "12345678-1234-5678-1234-56789abcdef6"

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self,
            bus,
            index,
            self.TEST_DESC_UUID,
            ["secure-read", "secure-write"],
            characteristic,
        )

    def ReadValue(self, options):
        return [dbus.Byte("E"), dbus.Byte("c"), dbus.Byte("h"), dbus.Byte("o")]


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.

    """

    CUD_UUID = "2901"

    def __init__(self, bus, index, characteristic):
        self.writable = "writable-auxiliaries" in characteristic.flags
        self.value = array.array("B", b"This is a characteristic for testing")
        self.value = self.value.tolist()
        Descriptor.__init__(
            self, bus, index, self.CUD_UUID, ["read", "write"], characteristic
        )

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value
