import os
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_main_db_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "data" / "markets.db"
        if candidate.exists():
            return candidate
    # Fallback (legacy layout)
    return here.parents[3] / "data" / "markets.db"


def get_main_db_path() -> Path:
    override = os.environ.get("MAIN_DB_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return _default_main_db_path()


@dataclass
class DbSnapshot:
    path: Path
    _tmp: tempfile.TemporaryDirectory

    def cleanup(self) -> None:
        self._tmp.cleanup()


def snapshot_main_db() -> DbSnapshot:
    src_path = get_main_db_path()
    if not src_path.exists():
        raise FileNotFoundError(f"Hlavní DB nenalezena: {src_path}")

    tmp = tempfile.TemporaryDirectory()
    dst_path = Path(tmp.name) / "markets.snapshot.db"

    src = sqlite3.connect(str(src_path))
    dst = sqlite3.connect(str(dst_path))
    try:
        src.backup(dst)
        dst.commit()
    finally:
        dst.close()
        src.close()

    return DbSnapshot(path=dst_path, _tmp=tmp)
