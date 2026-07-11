"""Tests for Parser."""

import pytest

from app.shell.parser import ParseError, Parser


def test_parse_valid_command_no_args() -> None:
    command = Parser().parse("pwd")
    assert command.name == "pwd"
    assert command.arguments == ()


def test_parse_valid_command_with_args() -> None:
    command = Parser().parse("cd cafe")
    assert command.name == "cd"
    assert command.arguments == ("cafe",)


def test_parse_unknown_command() -> None:
    with pytest.raises(ParseError):
        Parser().parse("fly")


def test_parse_too_many_arguments() -> None:
    with pytest.raises(ParseError):
        Parser().parse("pwd extra")


def test_parse_missing_required_argument() -> None:
    with pytest.raises(ParseError):
        Parser().parse("question")


def test_parse_empty_input() -> None:
    with pytest.raises(ParseError):
        Parser().parse("   ")