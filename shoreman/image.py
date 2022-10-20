from .git import find_latest_changes, get_commit_hash_for_ref, get_git_tags
from .log import log
from . import docker
from collections import namedtuple, defaultdict
from pathlib import Path
from .config import load_image_config


def find_changed_images(repo_path, prefix, ref):
    changed = {}
    image_dir = repo_path.joinpath(prefix)
    change_ref, changes = find_latest_changes(repo_path, ref)

    if not changes:
        log.debug("Unable to find any changes.")
        return get_commit_hash_for_ref(repo_path, ref), []

    for change in changes:
        changed_path = repo_path.joinpath(change)
        if changed_path.is_relative_to(image_dir):
            image_name = changed_path.relative_to(image_dir).parts[0]
            if image_dir.joinpath(image_name).joinpath("Dockerfile").exists():
                changed[image_name] = True
    if not len(changed):
        log.debug("no changed images found")
    return change_ref, list(changed.keys())


def parse_tag(line):
    splitter_index = line.rfind("-v")
    if splitter_index == -1:
        return None
    return line[:splitter_index], line[splitter_index + 2 :]


def get_tagged_images(repo_path, prefix, ref):
    image_dir = repo_path.joinpath(prefix)
    tags = []
    for tag in get_git_tags(repo_path, ref):
        image_name, image_version = parse_tag(tag)
        if image_dir.joinpath(image_name).joinpath("Dockerfile"):
            tags.append((image_name, image_version))
    images = set(t[0] for t in tags)
    return {i: [t[1] for t in tags if t[0] == i] for i in images}


ImageChange = namedtuple("ImageChange", ["name", "path", "ref", "tags"])


def get_changed_images(config):
    ref_hash = get_commit_hash_for_ref(config.repository_path, config.git_reference)
    _, changed_images = find_changed_images(
        config.repository_path, config.prefix, config.git_reference
    )
    tagged_images = get_tagged_images(
        config.repository_path, config.prefix, config.git_reference
    )
    changeset = []
    for image in changed_images:
        image_dir = config.repository_path.joinpath(config.prefix).joinpath(image)
        changeset.append(
            ImageChange(
                name=image,
                path=image_dir,
                ref=ref_hash,
                tags=tagged_images.get(image, []),
            )
        )
    return changeset


def get_all_images(config):
    ref_hash = get_commit_hash_for_ref(config.repository_path, config.git_reference)
    images = []
    for entry in config.repository_path.joinpath(config.prefix).iterdir():
        if not entry.is_dir():
            continue
        if (
            entry.joinpath("Dockerfile").exists()
            or entry.joinpath("image.conf").exists()
        ):
            images.append(
                ImageChange(
                    name=entry.name,
                    path=entry,
                    ref=ref_hash,
                    tags=[],
                )
            )
    return images


def resolve_tags(image_conf, image_change):
    tags = [*image_change.tags]
    has_tag = len(image_change.tags) != 0
    if has_tag and image_conf.tag_latest:
        tags.append("latest")

    if image_conf.tag_dev:
        tags.append("dev")

    if image_conf.tag_short_hash:
        tags.append(image_change.ref[:7])

    if image_conf.tag_long_hash:
        tags.append(image_change.ref)
    return tags


def create_build_targets(config, to_build):
    targets = {}
    for image_change in to_build:
        log.info("changed image name=%s", image_change.name)
        for tag in image_change.tags:
            log.info("new tag for image tag=%s:%s", image_change.name, tag)

        image_conf_path = image_change.path.joinpath("image.conf")
        image_conf = load_image_config(config.image_defaults_path, image_conf_path)
        tags = resolve_tags(image_conf, image_change)
        log.info("to build name=%s tags=%s", image_conf.fullname, ", ".join(tags))

        if not image_conf.enable_build:
            log.info("skipping disabled image name=%s", image_change.name)
            continue

        if not image_conf.registry or not image_conf.repository:
            log.info(
                "skipping because no registry/repository is defined name=%s",
                image_change.name,
            )
            continue

        targets[image_change.name] = docker.create_build_target(image_conf, tags)
    return targets
