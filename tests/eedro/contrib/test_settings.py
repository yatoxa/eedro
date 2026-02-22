from pathlib import Path

import pytest

from eedro.contrib import settings as settings_module
from eedro.contrib.settings import (
    CONFIG_PATH_ENV,
    SETTINGS_MODEL_ENV,
    BaseSettingsModel,
    ConfigFileNotFoundError,
    ImproperlyConfiguredError,
    LoadSettingsError,
    YamlSettingsModel,
    _get_config_path,
    _get_settings_model_class,
    _LazySettingsProxy,
)


class DemoSettings(BaseSettingsModel):
    value: int = 42

    @classmethod
    def load_settings(cls) -> "DemoSettings":
        return cls()


class BrokenSettings(BaseSettingsModel):
    @classmethod
    def load_settings(cls) -> "BrokenSettings":
        raise ValueError("boom")


def test_get_settings_model_class_uses_env(monkeypatch):
    monkeypatch.setenv(SETTINGS_MODEL_ENV, f"{__name__}.DemoSettings")

    assert _get_settings_model_class() is DemoSettings


def test_get_settings_model_class_requires_env(monkeypatch):
    monkeypatch.delenv(SETTINGS_MODEL_ENV, raising=False)

    with pytest.raises(ImproperlyConfiguredError):
        _get_settings_model_class()


def test_get_config_path_returns_existing_path(monkeypatch, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("debug: true\n")
    monkeypatch.setenv(CONFIG_PATH_ENV, str(config_path))

    assert _get_config_path(CONFIG_PATH_ENV) == config_path


def test_get_config_path_raises_when_missing(monkeypatch):
    missing = Path("/tmp/eedro-non-existent-config.yml")
    monkeypatch.setenv(CONFIG_PATH_ENV, str(missing))

    with pytest.raises(ConfigFileNotFoundError):
        _get_config_path(CONFIG_PATH_ENV)


def test_yaml_settings_model_load_settings(monkeypatch, tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("debug: true\n")
    monkeypatch.setenv(CONFIG_PATH_ENV, str(config_path))

    loaded = YamlSettingsModel.load_settings()
    assert loaded.debug is True


def test_lazy_settings_proxy_wraps_unexpected_exceptions(monkeypatch):
    monkeypatch.setenv(SETTINGS_MODEL_ENV, f"{__name__}.BrokenSettings")

    proxy = _LazySettingsProxy()
    with pytest.raises(LoadSettingsError):
        _ = proxy.debug


def test_lazy_settings_proxy_passthrough_settings_errors(monkeypatch):
    monkeypatch.delenv(SETTINGS_MODEL_ENV, raising=False)

    proxy = settings_module._LazySettingsProxy()
    with pytest.raises(ImproperlyConfiguredError):
        _ = proxy.debug
