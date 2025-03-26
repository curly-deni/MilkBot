import argparse

from .parser_command import *
from .parser_subcommands import *
from .parser_args import *


def cli_parser():
    parser = argparse.ArgumentParser(
        description="CLI tool to create project components."
    )
    command_parser = add_command_parser(parser)

    ### create command block
    create_command = add_create_command(command_parser)
    create_subparser = add_subcommand_parsers(create_command)
    # cog command
    add_module_param(
        add_type_param(add_name_param(add_cog_subcommand(create_subparser)))
    )
    # model command
    add_module_param(add_name_param(add_model_subcommand(create_subparser)))
    # migration command
    add_module_param(add_name_param(add_migration_subcommand(create_subparser)))
    # localization command
    # add_module_param(add_name_param(add_localization_subcommand(create_subparser)))
    # module command
    add_name_param(add_module_subcommand(create_subparser))

    ### migrate command block
    migrate_command = add_migrate_command(command_parser)
    migrate_subparser = add_subcommand_parsers(migrate_command)
    # up command
    add_module_param(add_id_or_head_param(add_up_subcommand(migrate_subparser)))
    # down command
    add_module_param(add_id_param(add_down_subcommand(migrate_subparser)))

    # setup command
    add_setup_command(command_parser)

    # update command
    add_update_command(command_parser)

    return parser
