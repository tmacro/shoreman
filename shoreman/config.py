import os
import pathlib
from collections import namedtuple
from configparser import ConfigParser

from .log import log

# Resolve path to included defaults
DEFAULTS = pathlib.Path(os.path.realpath(__file__)).parent.joinpath('defaults.conf')

def load_config(path):
    parser = ConfigParser(interpolation=None)
    parser.read([DEFAULTS, path])
    return
