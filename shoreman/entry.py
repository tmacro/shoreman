import argparse
import configparser
import logging
import os
import pathlib
import sys

from .command import commands
from .config import load_config
from .log import log, setLogLevel
from .util import path_type


def get_args():
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(sys.argv[0]).name,
        description='A tool for managing docker image repos',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config',
        default='~/.config/shoreman/shoreman.conf',
        type=path_type,
        help='Specify an alternate config file')

    parser.set_defaults(handler=None)

    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Don\'t execute any commands. Only log actions that would have been taken.')

    subparsers = parser.add_subparsers(title='Commands')
    version_subparser = subparsers.add_parser('version', help='Print program version')
    version_subparser.set_defaults(handler=commands.get('version'))

    args = parser.parse_args()
    if args.handler is None:
        parser.parse_args(['--help'])
    return args

def cli():
    args = get_args()
    config  = load_config(args.config)

    loglvl = os.environ.get('SM_LOGLVL', 'info')
    if args.verbose:
        loglvl = 'debug'

    if not hasattr(logging, loglvl):
        logging.error(f'Invalid log level: {loglvl}')
        sys.exit(1)

    setLogLevel(loglvl.upper())
    args.handler(args, config)
