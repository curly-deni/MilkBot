import argparse
import datetime
import json
import os
import re
import subprocess

from config import (
    STARTUP_MESSAGE,
    ORIGINAL_LOCALE,
    LIB_LOCALES,
    APP_LOCALES,
)

commands = {}


def command(name):
    def wrapper(func):
        commands[name] = {"func": func, "subcommands": {}}
        return func

    return wrapper


def subcommand(parent, name):
    def wrapper(func):
        if parent in commands:
            commands[parent]["subcommands"][name] = func
        return func

    return wrapper


templates = {
    "cog": """from module.cog import Cog

class {classname}(Cog):
    pass

def setup(bot):
    bot.add_cog({classname}(bot))
""",
    "model": """from sqlalchemy.orm import Mapped, mapped_column

from module.db_base import Base

class {classname}(Base):
    pass
""",
    "lib_model": """from sqlalchemy.orm import Mapped, mapped_column

from module.db_base import LBase

class {classname}(LBase):
    pass
""",
}


def get_module_path(name):
    if name == "app":
        return "app"
    elif name == "framecho":
        return "framecho/module"
    else:
        return f"module/{name}"


def to_snake_case(name):
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower()


def create_cog(name, is_folder, use_lib):
    name_snake_case = to_snake_case(name)
    base_path = "module" if use_lib else ""
    if is_folder:
        path = os.path.join(base_path, "cogs", name_snake_case)
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, "__init__.py")
    else:
        path = os.path.join(base_path, "cogs")
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f"{name_snake_case}.py")

    with open(file_path, "w") as f:
        f.write(templates["cog"].format(classname=name.capitalize()))

    print(f"Cog created at {file_path}")


def create_model(name, use_lib):
    name_snake_case = to_snake_case(name)
    base_path = "module" if use_lib else ""
    path = os.path.join(base_path, "models", f"{name_snake_case}.py")
    os.makedirs(os.path.join(base_path, "models"), exist_ok=True)
    with open(path, "w") as f:
        f.write(
            templates["model" if not use_lib else "lib_model"].format(
                classname=name.capitalize()
            )
        )
    print(f"Model created at {path}")


def create_migration(name, use_lib):
    try:
        alembic_args = (
            [
                "alembic",
                "-c",
                "module/alembic.ini",
                "revision",
                "--autogenerate",
                "-m",
                name,
            ]
            if use_lib
            else ["alembic", "revision", "--autogenerate", "-m", name]
        )
        subprocess.run(alembic_args, check=True)
        print(f"Alembic migration created with message: {name}")
    except subprocess.CalledProcessError as e:
        print(f"Error while running Alembic migration: {e}")


def migrate_up(revision="head", module_name="app"):
    try:
        alembic_args = [
            "alembic",
            "-c",
            f"{get_module_path(module_name)}/alembic.ini",
            "upgrade",
            revision,
        ]
        subprocess.run(alembic_args, check=True)
        print(f"Database migrated up to: {revision}")
    except subprocess.CalledProcessError as e:
        print(f"Error during alembic upgrade: {e}")


def migrate_down(revision, module_name="app"):
    try:
        alembic_args = [
            "alembic",
            "-c",
            f"{get_module_path(module_name)}/alembic.ini",
            "downgrade",
            revision,
        ]
        subprocess.run(alembic_args, check=True)
        print(f"Database migrated down to: {revision}")
    except subprocess.CalledProcessError as e:
        print(f"Error during alembic downgrade: {e}")


def prepare_locales(src_dir, dest_dir, src_locale, dest_locale):
    src_locale_dir = os.path.join(src_dir, src_locale)
    dest_locale_dir = os.path.join(dest_dir, dest_locale)

    print(f"Source dir: {src_locale_dir}")
    print(f"Destination dir: {dest_locale_dir}\n")
    print("Processing locales...")

    walk(
        dest_locale,
        src_locale_dir,
        src_locale,
        lambda src_file, dest_file: process_file(src_file, dest_file),
    )


def walk(locale, dir_path, src_locale, callback):
    for item in os.listdir(dir_path):
        full_path = os.path.join(dir_path, item)
        dest_path = full_path.replace(src_locale, locale)

        if os.path.isdir(full_path):
            walk(locale, full_path, src_locale, callback)
        else:
            callback(full_path, dest_path)


def process_file(src_file_path, dest_file_path):
    dest_file_dir = os.path.dirname(dest_file_path)
    os.makedirs(dest_file_dir, exist_ok=True)

    print(f"Source file: {src_file_path}")
    print(f"Destination file: {dest_file_path}\n")

    try:
        with open(src_file_path, "r", encoding="utf-8") as f:
            source_data = json.load(f)
    except Exception as e:
        raise Exception(f"Error reading source file: {src_file_path}") from e

    if os.path.exists(dest_file_path):
        try:
            with open(dest_file_path, "r", encoding="utf-8") as f:
                dest_data = json.load(f)
        except Exception as e:
            raise Exception(f"Error reading destination file: {dest_file_path}") from e

        for key in source_data:
            if key not in dest_data:
                dest_data[key] = ""

        with open(dest_file_path, "w", encoding="utf-8") as f:
            json.dump(dest_data, f, indent=2, ensure_ascii=False)  # noqa
    else:
        empty_data = {key: "" for key in source_data}
        with open(dest_file_path, "w", encoding="utf-8") as f:
            json.dump(empty_data, f, indent=2, ensure_ascii=False)  # noqa


# New update command
@command("update")
def update():
    migrate_up("head", "framecho")


@command("create")
def create(args):
    if args.subcommand in commands["create"]["subcommands"]:
        commands["create"]["subcommands"][args.subcommand](args)
    else:
        print("Unknown subcommand. Available: cog, model, migration, localization")
        return


@subcommand("create", "localization")
def localization_create(args):

    needle = LIB_LOCALES if args.module else APP_LOCALES
    dist_dir = src_dir = (
        os.path.join(os.path.dirname(__file__), "messages")
        if not args.module
        else os.path.join(os.path.dirname(__file__), "module", "messages")
    )

    for locale in needle:
        prepare_locales(src_dir, dist_dir, ORIGINAL_LOCALE, locale)


@subcommand("create", "cog")
def create_cog_command(args):
    create_cog(args.name, args.type == "folder", args.module)


@subcommand("create", "model")
def create_model_command(args):
    create_model(args.name, args.module)


@subcommand("create", "migration")
def create_migration_command(args):
    create_migration(args.name, args.module)


@command("migrate")
def migrate(args):
    if args.subcommand in commands["migrate"]["subcommands"]:
        commands["migrate"]["subcommands"][args.subcommand](args)
    else:
        print("Unknown subcommand for 'migrate'. Available: up, down")


@subcommand("migrate", "up")
def migrate_up_command(args):
    migrate_up(args.revision if args.revision else "head", args.module)


@subcommand("migrate", "down")
def migrate_down_command(args):
    migrate_down(args.revision, args.module)


def main():
    current_year = datetime.datetime.now().year

    print("Framecho - Enhanced Discord Framework")
    print(f"CLI (v0.1)")
    print(f"Copyright (c) 2025-{current_year} curly_deni (danila@dan-mi.ru)\n")

    print("--------")
    print(STARTUP_MESSAGE)
    print("--------\n")

    parser = argparse.ArgumentParser(
        description="CLI tool to create project components."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command and subcommands
    create_parser = subparsers.add_parser("create", help="Create a new component.")
    create_subparsers = create_parser.add_subparsers(
        dest="subcommand", help="Available subcommands"
    )

    cog_parser = create_subparsers.add_parser("cog", help="Create a new cog.")
    cog_parser.add_argument("name", help="Name of the cog.")
    cog_parser.add_argument(
        "-t", "--type", choices=["folder", "file"], required=True, help="Type of cog."
    )
    cog_parser.add_argument(
        "-m", "--module", help="Use module directory.", default="app"
    )

    localization_parser = create_subparsers.add_parser(
        "localization", help="Create or update localization files."
    )
    localization_parser.add_argument(
        "-m", "--module", help="Use module directory.", default="app"
    )

    model_parser = create_subparsers.add_parser("model", help="Create a new model.")
    model_parser.add_argument("name", help="Name of the model.")
    model_parser.add_argument(
        "-m", "--module", help="Use module directory.", default="app"
    )

    migration_parser = create_subparsers.add_parser(
        "migration", help="Create a new migration."
    )
    migration_parser.add_argument("name", help="Name of the migration.")
    migration_parser.add_argument(
        "-m", "--module", help="Use module directory.", default="app"
    )

    # Migrate command and subcommands
    migrate_parser = subparsers.add_parser("migrate", help="Migrate the database.")
    migrate_subparsers = migrate_parser.add_subparsers(
        dest="subcommand", help="Available subcommands"
    )

    up_parser = migrate_subparsers.add_parser("up", help="Upgrade the database.")
    up_parser.add_argument(
        "revision", nargs="?", help="Revision to upgrade to (default: head)."
    )
    up_parser.add_argument(
        "-m", "--module", help="Use module directory.", default="app"
    )

    down_parser = migrate_subparsers.add_parser("down", help="Downgrade the database.")
    down_parser.add_argument("revision", help="Revision to downgrade to.")
    down_parser.add_argument(
        "-m", "--module", help="Use module directory.", default="app"
    )

    # Update command
    subparsers.add_parser("update", help="Upgrade the database to the latest revision.")

    args = parser.parse_args()

    if not args.command or args.command not in commands:
        print("Invalid command or missing arguments.")
        parser.print_help()
        return

    if args.command == "create" and not args.subcommand:
        print("Invalid command or missing arguments.")
        create_parser.print_help()
        return

    if args.command == "migrate" and not args.subcommand:
        print("Invalid command or missing arguments.")
        migrate_parser.print_help()
        return

    if args.command == "update":
        commands["update"]["func"]()
        return

    commands[args.command]["func"](args)


if __name__ == "__main__":
    main()
