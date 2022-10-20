import os.path
import pathlib


def path_type(path):
    return pathlib.Path(os.path.expanduser(path)).resolve()


def path_type_relative(path):
    return pathlib.Path(os.path.expanduser(path))


class CommandRegistry:
    def __init__(self):
        self._commands = dict()

    def get(self, name):
        return self._commands[name]

    def register(self, name):
        def inner(func):
            if name in self._commands:
                raise ValueError(f"Command already registered: {name}")
            self._commands[name] = func
            return func

        return inner
