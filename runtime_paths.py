import os
from pathlib import Path
from typing import Union


def repo_root() -> Path:
    """
    Return the repository root, including when running from a git worktree under `.worktrees/`.
    """

    here = Path(__file__).resolve()
    if len(here.parents) >= 3 and ".worktrees" in here.parts:
        return here.parents[2]
    return here.parent


def resolve_repo_path(path: Union[str, Path]) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = repo_root() / p
    return p


def ensure_dir(path: Union[str, Path]) -> Path:
    p = resolve_repo_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
