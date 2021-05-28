#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

__all__ = [
    "BLUEZ_SERVICE_NAME",
    "GATT_MANAGER_IFACE",
    "DBUS_OM_IFACE",
    "DBUS_PROP_IFACE",
    "GATT_SERVICE_IFACE",
    "GATT_CHRC_IFACE",
    "GATT_DESC_IFACE",
    "LE_ADVERTISEMENT_IFACE",
    "LE_ADVERTISING_MANAGER_IFACE",
    "AGENT_INTERFACE",
    "AGENT_MANAGER_INTERFACE",
]

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE = "org.bluez.GattDescriptor1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
AGENT_INTERFACE = "org.bluez.Agent1"
AGENT_MANAGER_INTERFACE = "org.bluez.AgentManager1"
