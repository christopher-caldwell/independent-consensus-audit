"""PEP 517 shim that installs an ordinary wheel for editable requests.

Avoiding runtime path-file indirection keeps `uv run consensus-audit` behavior
consistent across Python environments while uv still rebuilds changed sources.
"""

from flit_core.buildapi import *  # noqa: F403
from flit_core import buildapi as _flit


def get_requires_for_build_editable(config_settings=None):
    return _flit.get_requires_for_build_wheel(config_settings)


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return _flit.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _flit.build_wheel(wheel_directory, config_settings, metadata_directory)
