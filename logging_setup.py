import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from runtime_paths import ensure_dir, env_flag, resolve_repo_path


def _parse_level(level: Optional[str]) -> int:
    value = (level or "").strip().upper()
    return getattr(logging, value, logging.INFO)


def setup_logging(service_name: str) -> None:
    """
    Configure root logging for the current process.

    - Always logs to stderr.
    - Optionally logs to a rotating file under `LOG_DIR` (defaults to `./logs`).
    """

    root = logging.getLogger()
    if getattr(root, "_polylab_configured", False):
        return

    level = _parse_level(os.environ.get("LOG_LEVEL", "INFO"))
    root.setLevel(level)

    fmt = os.environ.get(
        "LOG_FORMAT",
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    formatter = logging.Formatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    if env_flag("LOG_TO_FILE", default=True):
        log_dir = Path(os.environ.get("LOG_DIR", "logs"))
        if not log_dir.is_absolute():
            log_dir = resolve_repo_path(log_dir)
        try:
            ensure_dir(log_dir)
            log_path = log_dir / f"{service_name}.log"
            max_bytes = int(os.environ.get("LOG_MAX_BYTES", "2000000"))
            backup_count = int(os.environ.get("LOG_BACKUP_COUNT", "3"))
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except Exception:
            root.exception("Failed to set up file logging (continuing with stderr only).")

    root._polylab_configured = True
