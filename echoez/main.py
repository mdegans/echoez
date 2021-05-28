#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/
# some code from: https://punchthrough.com/creating-a-ble-peripheral-with-bluez/
# which is mostly also borrowed from the kernel source

import logging
import functools

import dbus
import dbus.mainloop.glib

from echoez.config import *
from echoez.app import App
from echoez.advertisement import EchoAdvertisement
from echoez.agent import Agent

try:
    from gi.repository import GLib  # pyright: reportMissingImports=false
except ImportError:
    import gobject as GLib  # pyright: reportMissingImports=false

__all__ = ["start"]

logger = logging.getLogger(__name__)


def on_register_success(thing: str):
    logger.info(f"GATT {thing} registered")


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def start(name: str) -> int:
    """Start Echoez service

    Args:
        name (str): to advertise to clients
    """
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    app = App(bus, name)
    loop = GLib.MainLoop()
    advertisement = EchoAdvertisement(bus, 0)
    agent = Agent(bus, name=name, loop=loop)

    gatt_obj = bus.get_object(BLUEZ_SERVICE_NAME, find_adapter(bus))
    if not gatt_obj:
        logger.error(f"Could not find {GATT_MANAGER_IFACE}")
        return -1
    bluez_obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")
    if not bluez_obj:
        logger.error("Could not get /org/bluez")

    adapter_props = dbus.Interface(gatt_obj, "org.freedesktop.DBus.Properties")

    # powered property on the controller to on
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    # Get manager objects
    service_manager = dbus.Interface(gatt_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(gatt_obj, LE_ADVERTISING_MANAGER_IFACE)
    agent_manager = dbus.Interface(bluez_obj, AGENT_MANAGER_INTERFACE)

    def on_register_failure(thing: str, error: GLib.Error):
        """error cb"""
        logger.error(f"Failed to register {thing} because: {str(error)}\n")
        loop.quit()

    logger.info("Registering GATT application...")
    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=functools.partial(on_register_success, "application"),
        error_handler=functools.partial(on_register_failure, "application"),
    )

    logger.info("Registering GATT advertisement...")
    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=functools.partial(on_register_success, "advertisement"),
        error_handler=functools.partial(on_register_failure, "advertisement"),
    )

    agent_manager.RegisterAgent(agent.path, "NoInputNoOutput")
    agent_manager.RequestDefaultAgent(agent.path)

    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info("quitting")
        loop.quit()
    try:
        ad_manager.UnregisterAdvertisement(advertisement)
        logger.info("Advertisement unregistered")
    except Exception as e:
        pass

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(0))

    return 0
