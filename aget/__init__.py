# -*- coding: utf-8 -*-

import sys
import os
import signal
import asyncio
import argparse
import logging

from .download import download
from .color import color_str
from .configure import configure
from .utils import assert_completed_file


def sigal_handler(signum, frame):
    print(color_str("  !! Signal:", codes=(1, 91)), signum)

    sys.exit(1)


def handle_signal():
    signal.signal(signal.SIGQUIT, sigal_handler)
    signal.signal(signal.SIGINT, sigal_handler)
    signal.signal(signal.SIGTERM, sigal_handler)


def parse_arguments(argv):
    p = argparse.ArgumentParser(description="")

    p.add_argument("url", type=str, help="")
    p.add_argument("-H", "--header", action="append", default=[], help="header")
    p.add_argument("-X", "--method", action="store", default="GET", type=str, help="")
    p.add_argument("-s", "--concurrency", action="store", default=None, type=int, help="")
    p.add_argument("-k", "--chuck_size", action="store", default=None, type=str, help="")
    p.add_argument("-d", "--data", action="store", default=None, type=str, help="")
    p.add_argument("-t", "--timeout", action="store", default=None, type=int, help="")
    p.add_argument("-q", "--quiet", action="store_true", default=False, help="")
    p.add_argument("-o", "--out", action="store", default=None, type=str, help="")

    args = p.parse_args(argv)

    return args


def main():
    # Set logging
    AGET_LOG_LEVEL = logging.CRITICAL
    log_level = os.getenv("AGET_LOG_LEVEL", "").upper()
    if hasattr(logging, log_level):
        AGET_LOG_LEVEL = getattr(logging, log_level)

    _format = "%(asctime)s %(levelname)s [%(name)s:%(lineno)s]: %(message)s"
    logging.basicConfig(format=_format, level=AGET_LOG_LEVEL)

    # Handle signals
    handle_signal()

    argv = sys.argv[1:]

    args = parse_arguments(argv)

    configure(args)

    assert_completed_file(args)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download(args))
