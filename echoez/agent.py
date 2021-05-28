#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

import logging

import dbus.service

from echoez.config import *
from echoez.err import *

try:
    from gi.repository import GLib  # pyright: reportMissingImports=false
except ImportError:
    import gobject as GLib  # pyright: reportMissingImports=fals

__all__ = [
    "Agent",
]

logger = logging.getLogger(__name__)


def set_trusted(path):
    bus = dbus.SystemBus()
    props = dbus.Interface(
        bus.get_object("org.bluez", path), "org.freedesktop.DBus.Properties"
    )
    props.Set("org.bluez.Device1", "Trusted", True)


# FIXME(mdegans): remove this. we want the app to be non-interactive
def ask(prompt):
    return input(prompt)


class Agent(dbus.service.Object):
    PATH_BASE = "/com/mdegans"

    def __init__(
        self, *args, loop: GLib.MainLoop = None, name: str = "echoez", **kwargs
    ):
        if not name.isalpha():
            raise ValueError(f"App name must be alphabetical only. '{name}' is invalid")

        self.path = f"{self.PATH_BASE}/{name}/agent"
        self.loop = loop
        dbus.service.Object.__init__(self, *args, object_path=self.path, **kwargs)

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        logger.info("Release")
        if self.loop:
            logger.info("Quitting GLib.MainLoop")
            self.loop.quit()

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        logger.info("AuthorizeService (%s, %s)" % (device, uuid))
        authorize = ask("Authorize connection (yes/no): ")
        if authorize == "yes":
            return
        raise RejectedException("Connection rejected by user")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        logger.info("RequestPinCode (%s)" % (device))
        set_trusted(device)
        return ask("Enter PIN Code: ")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        logger.info("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = ask("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        logger.info("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        logger.info("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        logger.info("RequestConfirmation (%s, %06d)" % (device, passkey))
        confirm = ask("Confirm passkey (yes/no): ")
        if confirm == "yes":
            set_trusted(device)
            return
        raise RejectedException("Passkey doesn't match")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        logger.info("RequestAuthorization (%s)" % (device))
        auth = ask("Authorize? (yes/no): ")
        if auth == "yes":
            return
        raise RejectedException("Pairing rejected")

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        logger.info("Cancel")
