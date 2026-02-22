import os
from functools import cached_property
from pathlib import Path
from typing import Any, Type

from pydantic_settings import BaseSettings
from yaml import full_load

from ..contrib.utils import import_string

SETTINGS_MODEL_ENV = "SETTINGS_MODEL"
CONFIG_PATH_ENV = "CONFIG_PATH"


class SettingsError(Exception):
    pass


class ImproperlyConfiguredError(SettingsError):
    pass


class ConfigFileNotFoundError(SettingsError):
    pass


class LoadSettingsError(SettingsError):
    pass


class BaseSettingsModel(BaseSettings):
    debug: bool = False

    @classmethod
    def load_settings(cls) -> "BaseSettingsModel":
        raise NotImplementedError


def _get_settings_model_class() -> Type[BaseSettingsModel]:
    try:
        return import_string(os.getenv(SETTINGS_MODEL_ENV))
    except (AttributeError, ImportError) as e:
        raise ImproperlyConfiguredError(
            f"The environment variable {SETTINGS_MODEL_ENV} must be defined"
            f" as a valid dotted and importable path to the settings model class."
        ) from e


def _get_config_path(config_path_env: str) -> Path:
    try:
        config_path = Path(os.getenv(config_path_env)).resolve()
    except TypeError as e:
        raise ImproperlyConfiguredError(
            f"The environment variable {config_path_env} must be defined"
            f" as a valid path to an existing YAML file."
        ) from e

    if config_path.exists():
        return config_path

    raise ConfigFileNotFoundError


class YamlSettingsModel(BaseSettingsModel):
    @classmethod
    def load_settings(cls) -> "YamlSettingsModel":
        with open(_get_config_path(CONFIG_PATH_ENV)) as config_file:
            return cls(**full_load(config_file))


class _LazySettingsProxy:
    @cached_property
    def _settings(self) -> BaseSettingsModel:
        try:
            return _get_settings_model_class().load_settings()
        except SettingsError:
            raise
        except Exception as e:
            raise LoadSettingsError from e

    def __getattr__(self, item: str) -> Any:
        return self.__dict__.setdefault(item, getattr(self._settings, item))


settings: BaseSettingsModel = _LazySettingsProxy()  # noqa
