from subprocess import run, CalledProcessError

from .utils import exit_when_module_not_exist, get_module_path

__all__ = ["migrate"]

subcommands = ["up", "down"]


def migrate(args):
    if args.subcommand not in subcommands:
        print("Unknown subcommand. Available: up, down")
        return
    exit_when_module_not_exist(args)
    globals()[f"migrate_{args.subcommand}"](args)


def migrate_up(args):
    revision = args.id
    module_path = get_module_path(args.module)

    try:
        alembic_args = [
            "alembic",
            "-c",
            f"{module_path}/alembic.ini",
            "upgrade",
            revision,
        ]
        run(alembic_args, check=True)
        print(f"Database migrated up to: {revision}")
    except CalledProcessError as e:
        print(f"Error during alembic upgrade: {e}")


def migrate_down(args):
    revision = args.id
    module_path = get_module_path(args.module)

    try:
        alembic_args = [
            "alembic",
            "-c",
            f"{module_path}/alembic.ini",
            "downgrade",
            revision,
        ]
        run(alembic_args, check=True)
        print(f"Database migrated down to: {revision}")
    except CalledProcessError as e:
        print(f"Error during alembic downgrade: {e}")
