__all__ = [
    "add_command_parser",
    "add_create_command",
    "add_migrate_command",
    "add_setup_command",
    "add_update_command",
]


def add_command_parser(parser):
    command_parser = parser.add_subparsers(dest="command", help="Available commands")
    return command_parser


def add_create_command(parser):
    create_parser = parser.add_parser("create", help="Create a new component.")
    return create_parser


def add_migrate_command(parser):
    migrate_parser = parser.add_parser("migrate", help="Run migrations.")
    return migrate_parser


def add_setup_command(parser):
    setup_parser = parser.add_parser("setup", help="Update project db.")
    return setup_parser


def add_update_command(parser):
    update_parser = parser.add_parser("update", help="Update the Framecho db.")
    return update_parser
