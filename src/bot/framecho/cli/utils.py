from os import path, getcwd
from pathlib import Path

from framecho.utils import camel_to_snake


def join_with_path(*args):
    return path.join(getcwd(), *args)


def get_module_path(name):
    if name == "app":
        return "app"
    elif name == "framecho":
        return path.join("framecho", "module")
    else:
        return path.join("modules", camel_to_snake(name))


def get_module_import_name(name):
    if name == "app":
        return "app"
    elif name == "framecho":
        return "framecho.module"
    else:
        return f"modules.{camel_to_snake(name)}"


def is_module_exist(module_path):
    _path = Path(join_with_path(module_path))  # noqa

    return _path.exists() and _path.is_dir() and (_path / "__init__.py").exists()


def exit_when_module_not_exist(args):
    module_path = get_module_path(args.module)

    if not is_module_exist(module_path):
        print(f"Module '{module_path}' does not exist.")
        exit(0)
