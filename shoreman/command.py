from .util import CommandRegistry
from . import __version__

commands = CommandRegistry()

@commands.register('version')
def version(args, config):
    print(f'shoreman v{__version__}')
    exit(0)
