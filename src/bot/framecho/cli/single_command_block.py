from dataclasses import dataclass
from os import getcwd
from pathlib import Path

from .migrate_command_block import migrate_up  # noqa

__all__ = ["setup", "update"]


@dataclass()
class LikeArgStruct:
    id: str
    module: str


def setup(args):  # noqa
    standart = ["app", "framecho"]

    for module in standart:
        _args = LikeArgStruct(id="head", module=module)
        try:
            migrate_up(_args)
        except Exception as e:
            print(f"Error during migration: {e}")

    modules_dir = Path(getcwd()) / "modules"
    if not modules_dir.exists():
        return

    for module in modules_dir.iterdir():
        if module.is_dir() and (module / "__init__.py").exists():
            _args = LikeArgStruct(id="head", module=module.name)
            try:
                migrate_up(_args)
            except Exception as e:
                print(f"Error during migration: {e}")


def update(args):  # noqa
    _args = LikeArgStruct(id="head", module="framecho")
    migrate_up(_args)
