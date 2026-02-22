from typing import Any


def import_string(dotted_path: str) -> Any:
    from importlib import import_module

    try:
        module_path, attribute_name = dotted_path.strip().rsplit(".", maxsplit=1)
    except ValueError as e:
        raise ImportError(f'"{dotted_path}" does not look like a module path') from e

    module = import_module(module_path)

    try:
        return getattr(module, attribute_name)
    except AttributeError as e:
        raise ImportError(
            f'Module "{module_path}" does not define a "{attribute_name}" attribute'
        ) from e
