"""Tests for promptdiff.cli — tests the init scaffolding command."""

import os
from click.testing import CliRunner
from promptdiff.cli import main


class TestInitCommand:
    def test_creates_file(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0
            assert os.path.exists("test_prompts.py")

    def test_file_contains_import(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            with open("test_prompts.py") as f:
                content = f.read()
            assert "from promptdiff import compare" in content

    def test_file_contains_model(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            with open("test_prompts.py") as f:
                content = f.read()
            assert 'model="gpt-4o-mini"' in content

    def test_custom_filename(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                main, ["init", "--filename", "my_test.py"]
            )
            assert result.exit_code == 0
            assert os.path.exists("my_test.py")

    def test_overwrite_confirmation(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create file first
            with open("test_prompts.py", "w") as f:
                f.write("existing content")
            # Run init — should prompt for confirmation
            result = runner.invoke(main, ["init"], input="y\n")
            assert result.exit_code == 0

    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_help_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "promptdiff" in result.output.lower()
