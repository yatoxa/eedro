from click.testing import CliRunner

from eedro.core.cli import main as main_module


class _RootPackage:
    __name__ = "demo_root_pkg"

    @staticmethod
    def get_version() -> str:
        return "1.2.3"


def _add_noop_subcommand(cmd):
    @cmd.command("noop")
    def _noop():
        return None

    return cmd


def test_main_cmd_configures_logging_when_not_quiet(monkeypatch):
    calls = {"enable": 0, "set_level": 0}

    def fake_enable_console_log(*, reset_logging_config):
        assert reset_logging_config is True
        calls["enable"] += 1

    def fake_set_log_level(self, logger=None, reset_logging_config=False):
        calls["set_level"] += 1

    monkeypatch.setattr(main_module, "enable_console_log", fake_enable_console_log)
    monkeypatch.setattr(main_module.LogLevel, "set_log_level", fake_set_log_level)

    cmd = _add_noop_subcommand(main_module.get_main_cmd(_RootPackage))
    result = CliRunner().invoke(cmd, ["noop"])

    assert result.exit_code == 0
    assert calls == {"enable": 1, "set_level": 1}


def test_main_cmd_quiet_disables_logging_setup(monkeypatch):
    calls = {"enable": 0, "set_level": 0}

    def fake_enable_console_log(*, reset_logging_config):
        calls["enable"] += 1

    def fake_set_log_level(self, logger=None, reset_logging_config=False):
        calls["set_level"] += 1

    monkeypatch.setattr(main_module, "enable_console_log", fake_enable_console_log)
    monkeypatch.setattr(main_module.LogLevel, "set_log_level", fake_set_log_level)

    cmd = _add_noop_subcommand(main_module.get_main_cmd(_RootPackage))
    result = CliRunner().invoke(cmd, ["--quiet", "noop"])

    assert result.exit_code == 0
    assert calls == {"enable": 0, "set_level": 0}


def test_main_cmd_version_option():
    cmd = main_module.get_main_cmd(_RootPackage)
    result = CliRunner().invoke(cmd, ["--version"])

    assert result.exit_code == 0
    assert "1.2.3" in result.output
