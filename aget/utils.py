# -*- coding: utf-8 -*-

import sys
import os
import struct

import mugen

from .color import color_str
from .common import (
    OneK,
    OneM,
    OneG,
    OneT,
    DEFAULT_CHUCK_SIZE
)


STRUCT_FORMAT = 'Q'   # unsigned long long


def make_headers(args):
    headers = {}
    for header in args.header:
        k, v = header.split(': ', 1)
        headers[k] = v
    return headers


def data_pack(num):
    return struct.pack(STRUCT_FORMAT, num)


def data_unpack(chuck):
    return struct.unpack(STRUCT_FORMAT, chuck)[0]


def exit_session():
    mugen.session().close()


def sizeof_fmt(num):
    for x in ['B','K','M','G']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'T')


def get_chuck_size(chuck_size_str):
    size = chuck_size_str.upper()
    if size.isdigit():
        return int(size)
    elif size.endswith('K'):
        s = int(size[:-1]) * OneK
        return s
    elif size.endswith('M'):
        s = int(size[:-1]) * OneM
        return s
    else:
        return DEFAULT_CHUCK_SIZE


def terminal_width():
    return int(os.popen('tput cols').read())


def assert_completed_file(args):
    path = args.out
    info_path = args.out + '.aget'
    if os.path.exists(path) and not os.path.exists(info_path):
        print(color_str(path, codes=(1, 91)), 'is existed')
        sys.exit()
