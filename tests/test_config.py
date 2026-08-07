"""Tests for the typed config loader.

The loader's job is to fail loudly on bad input, so most of these tests assert
that it raises — not that it succeeds.
"""

from dataclasses import dataclass

import pytest

import ragx
from ragx.config import ConfigError, load_config


@dataclass(frozen=True)
class DemoConfig:
    """A minimal schema used only to exercise the loader itself."""

    max_tokens: int
    overlap_tokens: int
    prepend_header: bool


def write(tmp_path, text: str):
    """Helper: drop a YAML file in pytest's per-test temp dir, return its path."""
    path = tmp_path / "demo.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_package_is_installed():
    """Guards against running the suite against an uninstalled source tree."""
    assert ragx.__version__ != "0.0.0+not-installed"


def test_loads_a_valid_file(tmp_path):
    cfg = load_config(
        write(tmp_path, "max_tokens: 384\noverlap_tokens: 64\nprepend_header: true\n"),
        DemoConfig,
    )
    assert cfg.max_tokens == 384
    assert cfg.overlap_tokens == 64
    assert cfg.prepend_header is True


def test_result_is_immutable(tmp_path):
    """frozen=True means a later stage can't quietly change what you logged."""
    cfg = load_config(
        write(tmp_path, "max_tokens: 384\noverlap_tokens: 64\nprepend_header: true\n"),
        DemoConfig,
    )
    with pytest.raises(Exception):
        cfg.max_tokens = 512  # type: ignore[misc]


def test_typo_in_key_is_caught(tmp_path):
    """The bug this whole module exists to prevent: `max_token` vs `max_tokens`."""
    with pytest.raises(ConfigError, match="unknown key"):
        load_config(
            write(tmp_path, "max_token: 384\noverlap_tokens: 64\nprepend_header: true\n"),
            DemoConfig,
        )


def test_missing_key_is_caught(tmp_path):
    with pytest.raises(ConfigError, match="missing key"):
        load_config(write(tmp_path, "max_tokens: 384\n"), DemoConfig)


def test_missing_file_is_caught(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.yaml", DemoConfig)


def test_empty_file_is_caught(tmp_path):
    """An empty YAML file parses to None, not to {} — easy to get wrong."""
    with pytest.raises(ConfigError, match="expected a mapping"):
        load_config(write(tmp_path, ""), DemoConfig)
