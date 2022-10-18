import sys
import pathlib
import logging

logging.basicConfig()
log = logging.getLogger(pathlib.Path(sys.argv[0]).name)

def setLogLevel(loglvl):
    if not hasattr(logging, loglvl):
        logging.error(f'Unknown log level: {loglvl}')
        raise ValueError(f'Unknown level: {loglvl}')
    log.setLevel(loglvl.upper())
