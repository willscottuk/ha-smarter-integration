"""The `version` module holds the version information for Smarter Kettle Client."""

from __future__ import annotations as _annotations

__all__ = "VERSION", "version_info"

VERSION = "0.3.0-dev.3"
"""The version of Smarter Kettle Client."""


def version_short() -> str:
    """Return the `major.minor` part of version.

    It returns '2.1' if version is '2.1.1'.
    """
    return ".".join(VERSION.split(".")[:2])


def version_info() -> str:
    """Return complete version information for package and its dependencies."""
    import platform
    import sys
    from pathlib import Path

    info = {
        "version": VERSION,
        "install path": Path(__file__).resolve().parent,
        "python version": sys.version,
        "platform": platform.platform(),
    }
    return "\n".join("{:>30} {}".format(k + ":", str(v).replace("\n", " ")) for k, v in info.items())
