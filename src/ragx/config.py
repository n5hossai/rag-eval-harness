"""Typed configuration loading.

Every knob in this project lives in a YAML file under `configs/`, never in a
function signature or a default argument. This module is the single place where
YAML text becomes a Python object.

Two rules are what make the experiment matrix tractable:

1.  Configs are DATA. Changing a setting is a data edit, not a code edit, so two
    runs are provably identical except for the thing you meant to change.
2.  Configs are FROZEN. Nothing deep in the pipeline can quietly mutate a setting
    mid-run, so the config you logged is guaranteed to be the config you ran.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, TypeVar

import yaml

# TypeVar lets load_config() tell the type checker "whatever dataclass you pass
# in, that's the type you get back" — so editors autocomplete the result.
T = TypeVar("T")

# Repo root, derived from this file's location: src/ragx/config.py -> up 3.
# Used to resolve paths in config files relative to the project, not to whatever
# directory the user happened to launch Python from.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(ValueError):
    """A YAML file did not match the dataclass it was supposed to fill.

    Its own exception type so callers can distinguish "your config is wrong"
    from "your code is wrong" — the first is a user error with a fixable cause,
    the second is a bug.
    """


def load_config(path: str | Path, schema: type[T]) -> T:
    """Read a YAML file and return it as an instance of `schema`.

    Args:
        path:   YAML file to read, e.g. configs/chunking.yaml
        schema: a frozen dataclass describing the keys that file must contain

    Returns:
        An instance of `schema` populated from the file.

    Raises:
        ConfigError: file missing, not a mapping, or keys don't match `schema`.

    The point of this function is that it FAILS LOUDLY. A typo like `max_token`
    instead of `max_tokens` raises here, at load time, with the file name in the
    message — rather than silently falling back to a default and producing a
    quietly wrong number that surfaces days later, if at all.
    """
    if not is_dataclass(schema):
        raise ConfigError(f"{schema.__name__} is not a dataclass")

    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")

    # safe_load (not load) refuses to construct arbitrary Python objects from
    # the YAML. Always safe_load when reading files you might not control.
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))

    # An empty file parses to None; a list or scalar parses to the wrong shape.
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: expected a mapping at the top level, got {type(raw).__name__}")

    expected = {f.name for f in fields(schema)}
    got = set(raw)

    # Report BOTH directions of mismatch. Unknown keys usually mean a typo or a
    # config left over from an earlier revision; missing keys mean the schema
    # grew and this file wasn't updated to match.
    if unknown := got - expected:
        raise ConfigError(f"{path}: unknown key(s) {sorted(unknown)}; expected {sorted(expected)}")
    if missing := expected - got:
        raise ConfigError(f"{path}: missing key(s) {sorted(missing)}")

    # ** unpacks the dict into keyword arguments:
    #     schema(max_tokens=384, overlap_tokens=64, ...)
    return schema(**raw)
