import os
from functools import cached_property
from pathlib import Path
from typing import Any, Type

from pydantic.v1 import BaseSettings
from pydantic.v1.utils import import_string
from yaml import full_load

SETTINGS_MODEL_ENV = "SETTINGS_MODEL"
CONFIG_PATH_ENV = "CONFIG"


class SettingsError(Exception):
    pass


class ImproperlyConfiguredError(SettingsError):
    pass


class ConfigFileNotFoundError(SettingsError):
    pass


class LoadSettingsError(SettingsError):
    pass


class CommonSettings(BaseSettings):
    debug: bool = False


def _get_settings_model_class() -> Type[CommonSettings]:
    try:
        return import_string(os.getenv(SETTINGS_MODEL_ENV))
    except (AttributeError, ImportError) as e:
        raise ImproperlyConfiguredError(
            f"The environment variable {SETTINGS_MODEL_ENV} must be defined"
            f" as a valid dotted and importable path to the settings model class."
        ) from e


def _get_config_path() -> Path:
    try:
        config_path = Path(os.getenv(CONFIG_PATH_ENV))
    except TypeError as e:
        raise ImproperlyConfiguredError(
            f"The environment variable {CONFIG_PATH_ENV} must be defined"
            f" as a valid path to an existing YAML file."
        ) from e

    if config_path.exists():
        return config_path

    raise ConfigFileNotFoundError


def _load_from_yaml() -> CommonSettings:
    try:
        with open(_get_config_path()) as config_file:
            return _get_settings_model_class()(**full_load(config_file))
    except SettingsError:
        raise
    except Exception as e:
        raise LoadSettingsError from e


class _LazySettingsProxy:
    @cached_property
    def _settings(self) -> CommonSettings:
        return _load_from_yaml()

    def __getattr__(self, item: str) -> Any:
        return self.__dict__.setdefault(item, getattr(self._settings, item))


settings: CommonSettings = _LazySettingsProxy()  # noqa
