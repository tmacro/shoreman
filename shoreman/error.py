class ShoremanError(Exception):
    pass


class FailedCommandError(ShoremanError):
    def __init__(self, cmd):
        errmsg = f"Failed to run command: {cmd}"
        super().__init__(errmsg)
        self.cmd = cmd
