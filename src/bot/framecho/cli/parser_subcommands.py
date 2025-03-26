__all__ = [
    "add_subcommand_parsers",
    "add_cog_subcommand",
    "add_model_subcommand",
    "add_migration_subcommand",
    "add_module_subcommand",
    "add_up_subcommand",
    "add_down_subcommand",
]


def add_subcommand_parsers(parser):
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")
    return subparsers


def add_cog_subcommand(parser):
    cog_parser = parser.add_parser("cog", help="Create a new cog.")
    return cog_parser


def add_model_subcommand(parser):
    model_parser = parser.add_parser("model", help="Create a new model.")
    return model_parser


def add_migration_subcommand(parser):
    migration_parser = parser.add_parser("migration", help="Create a new migration.")
    return migration_parser


def add_module_subcommand(parser):
    module_parser = parser.add_parser("module", help="Create a new module.")
    return module_parser


def add_up_subcommand(parser):
    up_parser = parser.add_parser("up", help="Run migrations up.")
    return up_parser


def add_down_subcommand(parser):
    down_parser = parser.add_parser("down", help="Run migrations down.")
    return down_parser
