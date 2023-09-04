import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values


def is_docker() -> bool:
    path = "/proc/self/cgroup"
    return os.path.exists("/.dockerenv") or (
        os.path.isfile(path) and any("docker" in line for line in open(path))
    )


def read_env(path: Path, read_from_file: bool = True) -> Dict[str, Optional[str]]:
    if is_docker() or read_from_file is False:
        return {**os.environ}
    return {**dotenv_values(path)}
