from .shell import get_stdout, run_cmd
from .log import log
from .error import FailedCommandError


def get_commit_changes(repo, ref):
    cmd = f"git diff --name-only {ref}^ {ref} --"
    rc, changes = get_stdout(cmd, cwd=repo)
    if rc != 0:
        log.error("Failed to get changes for ref %s", ref)
        raise FailedCommandError(cmd)
    return changes


def get_git_tags(repo, ref):
    cmd = f"git tag --points-at {ref}"
    rc, tag_list = get_stdout(cmd, cwd=repo)
    if rc != 0:
        log.error("Failed to get git tags for HEAD")
        raise FailedCommandError(cmd)
    return tag_list


def get_commit_refs(repo, ref):
    cmd = f"git log  --max-count=100 '--pretty=%H' {ref}"
    rc, refs = get_stdout(cmd, cwd=repo)
    if rc != 0:
        log.error("Failed to list references")
        raise FailedCommandError(cmd)
    return refs


def fetch_git_history(repo):
    cmd = "git fetch --unshallow"
    rc = run_cmd(cmd, cwd=repo)
    if rc != 1:
        log.error("Failed to unshallow repo")
        raise FailedCommandError(cmd)


def is_shallow_repo(repo):
    cmd = f"git rev-parse --is-shallow-repository"
    rc, output = get_stdout(cmd, cwd=repo)
    if rc != 0:
        log.error("Failed to check if repo is shallow")
        raise FailedCommandError(cmd)
    return output.strip() == "true"


def get_commit_hash_for_ref(repo, ref):
    cmd = f"git rev-parse {ref}"
    rc, output = get_stdout(cmd, cwd=repo)
    if rc != 0:
        log.error("Failed to get hash for ref %s", ref)
        raise FailedCommandError(cmd)
    return output[0]


def iter_commit_refs(repo, start_ref):
    refs = get_commit_refs(repo, start_ref)
    while True:
        for ref in refs:
            yield ref
        last_ref = refs[-1]
        refs = get_commit_refs(repo, last_ref)
        if not refs or refs == [last_ref]:
            break
        refs = refs[1:]


def find_latest_changes(repo, reference):
    log.debug("looking for changes starting at %s", reference)
    changes = get_commit_changes(repo, reference)
    if len(changes):
        log.debug("found changes in given ref")
        return get_commit_hash_for_ref(repo, reference), changes
    if is_shallow_repo(repo):
        fetch_git_history(repo)
    for ref in iter_commit_refs(repo, f"{reference}^"):
        changes = get_commit_changes(repo, ref)
        if len(changes):
            log.debug("found changes at ref %s", ref)
            return ref, changes
