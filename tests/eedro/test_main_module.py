import runpy
import sys
import types


class _DummyCommand:
    def __init__(self) -> None:
        self.commands = []
        self.called = 0

    def add_command(self, command) -> None:
        self.commands.append(command)

    def __call__(self) -> None:
        self.called += 1


def test_main_module_registers_startproject_and_executes_command(monkeypatch):
    dummy_main_cmd = _DummyCommand()
    dummy_startproject_cmd = object()

    monkeypatch.setitem(
        sys.modules,
        "eedro.core.cli.main",
        types.SimpleNamespace(main_cmd=dummy_main_cmd),
    )
    monkeypatch.setitem(
        sys.modules,
        "eedro.core.cli.startproject.command",
        types.SimpleNamespace(startproject_cmd=dummy_startproject_cmd),
    )
    monkeypatch.delitem(sys.modules, "eedro.__main__", raising=False)

    runpy.run_module("eedro.__main__", run_name="__main__")

    assert dummy_main_cmd.commands == [dummy_startproject_cmd]
    assert dummy_main_cmd.called == 1
