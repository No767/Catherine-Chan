from pkgutil import iter_modules
from typing import Literal, NamedTuple


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "final"]

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.micro}-{self.releaselevel}"


EXTENSIONS = [module.name for module in iter_modules(__path__, f"{__package__}.")]
VERSION: VersionInfo = VersionInfo(major=1, minor=0, micro=0, releaselevel="beta")
