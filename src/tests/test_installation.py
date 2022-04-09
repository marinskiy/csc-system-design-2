"""Checks that roguelike is installed with py version"""

import sys

import pkg_resources


def test_python_version() -> None:
    assert sys.version.startswith('3.8.11')


def test_cli_is_installed() -> None:
    assert 'roguelike' in pkg_resources.working_set.by_key  # type: ignore
