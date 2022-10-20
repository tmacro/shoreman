import argparse
import configparser
import logging
import os
import pathlib
import sys
import textwrap

from .command import commands
from .config import load_config
from .log import log, setLogLevel
from .util import path_type_relative, path_type


def get_args():
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(sys.argv[0]).name,
        description="A tool for managing docker image repos",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--config",
        default="shoreman.conf",
        type=path_type_relative,
        help=textwrap.dedent(
            """\
            Specify an alternate config file relative to the repository root
            (default: shoreman.conf)
        """
        ),
        dest="config_path",
    )

    parser.add_argument(
        "-r",
        "--repo",
        default=".",
        type=path_type,
        help=textwrap.dedent(
            """\
            Path to the git repository to operate on
            (default: .)
        """
        ),
        dest="repo_path",
    )

    parser.add_argument(
        "-p",
        "--prefix",
        default=".",
        type=path_type_relative,
        help="Relative path to the directory containing images",
    )

    parser.add_argument(
        "--ref", default="HEAD", help="Git reference to inspect.", dest="git_ref"
    )

    parser.set_defaults(handler=None)

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Don't execute any commands. Only log actions that would have been taken.",
    )

    subparsers = parser.add_subparsers(title="Commands")
    version_subparser = subparsers.add_parser("version", help="Print program version")
    version_subparser.set_defaults(handler=commands.get("version"))

    changes_subparser = subparsers.add_parser(
        "changes", help="Print detected image changes"
    )
    changes_subparser.set_defaults(handler=commands.get("changes"))

    build_subparser = subparsers.add_parser("build", help="Build changed images")
    build_subparser.set_defaults(handler=commands.get("build"))
    build_subparser.add_argument(
        "--all",
        action="store_true",
        help="Build all images regardless of changes",
        dest="build_all",
    )
    build_subparser.add_argument(
        "--push", action="store_true", help="Push images after building"
    )

    args = parser.parse_args()
    if args.handler is None:
        parser.parse_args(["--help"])
    return args


def cli():
    args = get_args()
    if not args.config_path.is_absolute():
        config_path = args.repo_path.joinpath(args.config_path)
    else:
        config_path = args.config_path

    config = load_config(args, config_path)

    loglvl = os.environ.get("SM_LOGLVL", "info")
    if args.verbose:
        loglvl = "debug"

    if not hasattr(logging, loglvl):
        logging.error(f"Invalid log level: {loglvl}")
        sys.exit(1)

    setLogLevel(loglvl.upper())
    args.handler(args, config)
