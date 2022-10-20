import subprocess
import shlex

from .log import log


def splitlines(text):
    return [line.strip() for line in text.split("\n") if len(line.strip())]


def run(cmd, cwd=None, stdout=False, stderr=False, dry_run=False):
    capture_output = stdout or stderr
    log.debug("running command: %s", cmd)
    if cwd:
        log.debug("using cwd: %s", cwd)
    if dry_run:
        log.debug("skipping due to dry run")
        if capture_output:
            return 0, []
        return 0

    proc = subprocess.run(
        shlex.split(cmd), cwd=cwd, capture_output=capture_output, encoding="utf-8"
    )

    log.debug("cmd exited: %i", proc.returncode)

    if proc.returncode != 0:
        if capture_output:
            print(proc.stderr)
            return proc.returncode, None
        return proc.returncode

    if capture_output:
        # If both stderr and stdout the output is combined on stdout
        if stderr:
            stream = proc.stderr
        if stdout:
            stream = proc.stdout
        return 0, splitlines(stream)
    return 0


def run_cmd(*args, **kwargs):
    return run(*args, **kwargs)


def get_stdout(*args, **kwargs):
    return run(*args, stdout=True, **kwargs)


def get_stderr(*args, **kwargs):
    return run(*args, stderr=True, **kwargs)


def get_output(*args, **kwargs):
    return run(*args, stdout=True, stderr=True, **kwargs)
