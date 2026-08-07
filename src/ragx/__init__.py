"""ragx — an evaluation harness for retrieval-augmented generation.

The package is deliberately organised around the two-layer model: retrieval and
generation are separate concerns that fail independently and are measured
independently.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    # Read the version from the installed package metadata (pyproject.toml).
    # Doing it this way means the version lives in exactly one place and can
    # never drift out of sync with what pip installed.
    __version__ = version("ragx")
except PackageNotFoundError:  # pragma: no cover
    # Reached only if someone imports the source tree without installing it.
    __version__ = "0.0.0+not-installed"

__all__ = ["__version__"]
