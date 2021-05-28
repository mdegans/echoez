#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

import dbus.service

from echoez.config import *
from echoez.err import *
from echoez.descriptor import (
    EchoDescriptor,
    EchoEncryptDescriptor,
    EchoSecureDescriptor,
    CharacteristicUserDescriptionDescriptor,
)

__all__ = [
    "Characteristic",
    "EchoCharacteristic",
    "EchoEncryptCharacteristic",
    "EchoSecureCharacteristic",
]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """

    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + "/char" + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
                "Descriptors": dbus.Array(self.get_descriptor_paths(), signature="o"),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        print("Default ReadValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        print("Default WriteValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print("Default StartNotify called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print("Default StopNotify called, returning error")
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class EchoCharacteristic(Characteristic):
    """
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

    """

    TEST_CHRC_UUID = "12345678-1234-5678-1234-56789abcdef1"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self,
            bus,
            index,
            self.TEST_CHRC_UUID,
            ["read", "write", "writable-auxiliaries"],
            service,
        )
        self.value = []
        self.add_descriptor(EchoDescriptor(bus, 0, self))
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        print("TestCharacteristic Read: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("TestCharacteristic Write: " + repr(value))
        self.value = value


class EchoEncryptCharacteristic(Characteristic):
    """
    Dummy test characteristic requiring encryption.

    """

    TEST_CHRC_UUID = "12345678-1234-5678-1234-56789abcdef3"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self,
            bus,
            index,
            self.TEST_CHRC_UUID,
            ["encrypt-read", "encrypt-write"],
            service,
        )
        self.value = []
        self.add_descriptor(EchoEncryptDescriptor(bus, 2, self))
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print("TestEncryptCharacteristic Read: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("TestEncryptCharacteristic Write: " + repr(value))
        self.value = value


class EchoSecureCharacteristic(Characteristic):
    """
    Dummy test characteristic requiring secure connection.

    """

    TEST_CHRC_UUID = "12345678-1234-5678-1234-56789abcdef5"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self,
            bus,
            index,
            self.TEST_CHRC_UUID,
            ["secure-read", "secure-write"],
            service,
        )
        self.value = []
        self.add_descriptor(EchoSecureDescriptor(bus, 2, self))
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print("TestSecureCharacteristic Read: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("TestSecureCharacteristic Write: " + repr(value))
        self.value = value
