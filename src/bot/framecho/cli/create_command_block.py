from pathlib import Path
from subprocess import run, CalledProcessError

from framecho.utils import camel_to_snake
from .create_templates import *
from .utils import (
    get_module_path,
    get_module_import_name,
    join_with_path,
    exit_when_module_not_exist,
    is_module_exist,
)

__all__ = ["create"]

subcommands = ["cog", "model", "migration", "localization", "module"]


def create_migration_folder(module_name):
    module_name_snake_case = camel_to_snake(module_name)
    module_path = get_module_path(module_name)
    module_import_name = get_module_import_name(module_name)

    _module_path = Path(join_with_path(module_path))

    if not (_module_path / "migration").exists():
        (_module_path / "migration").mkdir(parents=True, exist_ok=True)

    if not (_module_path / "migration" / "env.py").exists():
        with open(_module_path / "migration" / "env.py", "w+") as f:
            f.write(
                migration_env_py_template.replace(
                    "{module_import_name}", module_import_name
                ).replace("{module_name}", module_name_snake_case)
            )

    if not (_module_path / "migration" / "script.py.mako").exists():
        with open(_module_path / "migration" / "script.py.mako", "w+") as f:
            f.write(migration_script_py_mako)

    if not (_module_path / "migration" / "versions").exists():
        (_module_path / "migration" / "versions").mkdir(parents=True, exist_ok=True)

    if not (_module_path / "migration" / "versions" / "__init__.py").exists():
        with open(
            _module_path / "migration" / "versions" / "__init__.py", "w+"
        ) as f:  # noqa
            ...

    if not (_module_path / "alembic.ini").exists():
        with open(_module_path / "alembic.ini", "w+") as f:
            f.write(migration_alembic_ini_template.format(module_path=module_path))


def create_cogs_folder(module_name):
    module_path = get_module_path(module_name)
    _module_path = Path(join_with_path(module_path))

    if not (_module_path / "cogs").exists():
        (_module_path / "cogs").mkdir(parents=True, exist_ok=True)


def create_models_folder(module_name):
    module_name_snake_case = camel_to_snake(module_name)
    module_path = get_module_path(module_name)
    _module_path = Path(join_with_path(module_path))

    if not (_module_path / "models").exists():
        (_module_path / "models").mkdir(parents=True, exist_ok=True)

    if not (_module_path / "models" / "base.py").exists():
        with open(_module_path / "models" / "base.py", "w+") as f:
            f.write(
                base_model_template.replace("{module_name}", module_name_snake_case)
            )


def create(args):
    if args.subcommand not in subcommands:
        print(
            "Unknown subcommand. Available: cog, model, migration, localization, module"
        )
        return
    if args.subcommand != "module":
        exit_when_module_not_exist(args)
    globals()[f"create_{args.subcommand}"](args)


def create_cog(args):
    create_cogs_folder(args.module)
    cogs_path = Path(join_with_path(get_module_path(args.module), "cogs"))
    snake_name = camel_to_snake(args.name)
    is_folder = args.type == "folder"

    if is_folder:
        (cogs_path / snake_name).mkdir(parents=True, exist_ok=True)
        file_path = cogs_path / snake_name / "__init__.py"
    else:
        file_path = cogs_path / f"{snake_name}.py"

    with open(file_path, "w+") as f:
        f.write(cog_template.format(class_name=args.name))

    print(f"Cog created at {file_path}")


def create_model(args):
    create_models_folder(args.module)
    models_path = Path(join_with_path(get_module_path(args.module), "models"))
    snake_name = camel_to_snake(args.name)

    with open(models_path / f"{snake_name}.py", "w+") as f:
        f.write(model_template.format(class_name=args.name))

    print(f"Model created at {models_path / f'{snake_name}.py'}")


def create_migration(args):
    create_migration_folder(args.module)
    module_path = get_module_path(args.module)

    try:
        alembic_args = [
            "alembic",
            "-c",
            f"{module_path}/alembic.ini",
            "revision",
            "--autogenerate",
            "-m",
            args.name,
        ]
        run(alembic_args, check=True)
        print(f"Alembic migration created with message: {args.name}")
    except CalledProcessError as e:
        print(f"Error while running Alembic migration: {e}")


def create_module(args):
    module_path = get_module_path(args.name)

    if is_module_exist(module_path):
        print(f"Module '{module_path}' already exists.")
        return

    _module_path = Path(join_with_path(module_path))
    _module_path.mkdir(parents=True, exist_ok=True)

    with open(_module_path / "__init__.py", "w+") as f:  # noqa
        ...

    create_migration_folder(args.name)
    create_cogs_folder(args.name)
    create_models_folder(args.name)
