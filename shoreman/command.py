from pprint import pprint

from . import __version__, docker
from .image import get_changed_images, get_all_images, create_build_targets
from .config import load_image_config
from .log import log
from .util import CommandRegistry
from .error import FailedCommandError

commands = CommandRegistry()


@commands.register("version")
def version(args, config):
    print(f"shoreman v{__version__}")
    exit(0)


@commands.register("changes")
def changes(args, config):
    changeset = get_changed_images(config)
    for change in changeset:
        log.info("changed image name=%s", change.name)
        for tag in change.tags:
            log.info("new tag for image tag=%s:%s", change.name, tag)
    exit(0)


@commands.register("build")
def build(args, config):

    if args.build_all:
        to_build = get_all_images(config)
    else:
        to_build = get_changed_images(config)

    targets = create_build_targets(config, to_build)

    if not len(targets):
        log.info("exiting because no images were selected to build")
        exit(0)

    failed_builds = []
    for name, target in targets.items():
        build_def = docker.create_build_definition({name: target})
        try:
            docker.bake_image(build_def, push=args.push, dry_run=config.dry_run)
        except FailedCommandError:
            log.error("build failed for %s", name)
    for name in targets.keys():
        if name not in failed_builds:
            log.info("built image for %s", name)
        else:
            log.info("failed to build image %s", name)
    exit(0)
