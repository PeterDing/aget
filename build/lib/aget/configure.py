# -*- coding: utf-8 -*-

import os
import configparser
import urllib

from .utils import get_chuck_size


DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(__file__), 'config')

USER_CONFIG_FILE = os.path.join(
    os.path.expanduser('~'), 'config')


def configure(args):
    if os.path.exists(USER_CONFIG_FILE):
        config_file = USER_CONFIG_FILE
    else:
        config_file = DEFAULT_CONFIG_FILE

    assert os.path.exists(config_file), '{} is not existed'.format(config_file)

    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.read(config_file)

    if not args.concurrency:
        concurrency = int(config_parser['basic']['concurrency'])
        args.concurrency = concurrency

    if not args.chuck_size:
        chuck_size = get_chuck_size(config_parser['basic']['chuck_size'])
        args.chuck_size = chuck_size
    else:
        chuck_size = get_chuck_size(args.chuck_size)
        args.chuck_size = chuck_size

    if not args.header:
        args.header = ['User-Agent: ' + config_parser['http']['user-agent'] or 'aget']

    if config_parser['basic']['quiet'] == 'true':
        args.quiet = True

    if args.data:
        args.method = 'POST'

    if not args.out:
        url_parser = urllib.parse.urlparse(args.url)
        path = url_parser.path.strip('/')
        if not path:
            raise IOError('Can not get filename')
        else:
            args.out = path.split('/')[-1]
