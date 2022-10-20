from collections import namedtuple
import json
import tempfile
from .shell import run_cmd
from .log import log


def create_build_target(image_config, tags):
    return {
        "dockerfile": image_config.dockerfile.as_posix(),
        "context": image_config.context.as_posix(),
        "tags": [f"{image_config.fullname}:{tag}" for tag in tags],
        "platforms": image_config.platforms,
    }


def create_build_definition(targets):
    return {
        "group": {"build": {"targets": list(targets.keys())}},
        "target": targets,
    }


def bake_image(build_definition, push=False, dry_run=False):
    with tempfile.NamedTemporaryFile(
        mode="w", prefix="docker-build-def-", suffix=".json"
    ) as f:
        cmd = f'docker buildx bake -f={f.name} build --progress=plain --pull {"--push" if push else ""}'
        if not dry_run:
            json.dump(build_definition, f)
            f.flush()
            run_cmd(cmd)
        else:
            log.info("skipping docker build due to dry_run")
