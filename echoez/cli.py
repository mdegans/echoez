#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/

"""Console script for echoez."""

import argparse
import logging
import sys

from typing import (
    Sequence,
    Optional,
)

import echoez.main


def cli_main(args: Optional[Sequence[str]] = None):
    """Console entrypoint for Echoez."""
    parser = argparse.ArgumentParser(
        description="Simple Bluetooth Low Energy Echo Server"
    )
    parser.add_argument("--name", help="to advertise service as", default="echoez")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args(args)

    # setup logging
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    del args.verbose

    return echoez.main.start(**vars(args))


if __name__ == "__main__":
    sys.exit(cli_main())  # pragma: no cover
