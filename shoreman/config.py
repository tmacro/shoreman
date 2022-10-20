import os
import sys
from pathlib import Path
from collections import namedtuple
from configparser import ConfigParser

from .log import log

# Resolve path to included defaults
BUILTIN_DEFAULTS = Path(os.path.realpath(__file__)).parent.joinpath("defaults.conf")

ImageConfig = namedtuple(
    "ImageConfig",
    [
        "name",
        "fullname",
        "repository",
        "registry",
        "platforms",
        "dockerfile",
        "context",
        "tag_latest",
        "tag_dev",
        "tag_short_hash",
        "tag_long_hash",
        "enable_build",
    ],
)


def load_image_config(defaults_path, path):
    parser = ConfigParser(interpolation=None)
    parser.read([BUILTIN_DEFAULTS, defaults_path, path])

    image_dir = Path(path).parent

    if parser.has_option("image", "name"):
        name = parser.get("image", "name")
    else:
        name = image_dir.name

    registry = parser.get("image", "registry", fallback=None)
    repository = parser.get("image", "repository", fallback=None)

    if registry is None:
        log.warn("You must set a registry before you can build")

    if repository is None:
        log.warn("You must set a repository before you can build")

    fullname = f"{registry}/{repository}/{name}"

    platforms = [p.strip() for p in parser.get("image", "platforms").split(",")]

    if parser.has_option("image", "dockerfile"):
        dockerfile = parser.get("image", "dockerfile")
    else:
        dockerfile = image_dir.joinpath("Dockerfile")

    return ImageConfig(
        name=name,
        fullname=fullname,
        repository=repository,
        registry=registry,
        platforms=platforms,
        dockerfile=dockerfile,
        context=image_dir,
        tag_latest=parser.getboolean("image", "tag_latest"),
        tag_dev=parser.getboolean("image", "tag_dev"),
        tag_long_hash=parser.getboolean("image", "tag_long_hash"),
        tag_short_hash=parser.getboolean("image", "tag_short_hash"),
        enable_build=parser.getboolean("image", "enable_build"),
    )


GithubConfig = namedtuple("Config", ["work_dir"])


def load_github_conf():
    return GithubConfig(work_dir=os.environ.get("GITHUB_WORKSPACE"))


ShoremanConfig = namedtuple(
    "ShoremanConfig",
    [
        "repository_path",
        "prefix",
        "dry_run",
        "verbose",
        "image_defaults_path",
        "git_reference",
    ],
)


def load_config(args, path):
    parser = ConfigParser(interpolation=None)
    parser.read([BUILTIN_DEFAULTS, path])
    return ShoremanConfig(
        repository_path=args.repo_path,
        prefix=args.prefix or parser.get("shoreman", "prefix", fallback="."),
        dry_run=args.dry_run
        or parser.getboolean("shoreman", "dry_run", fallback=False),
        verbose=args.verbose
        or parser.getboolean("shoreman", "verbose", fallback=False),
        image_defaults_path=path,
        git_reference=args.git_ref,
    )
