"""SLAI CLI — Supply chain load management from your terminal."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("slai-cli")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
