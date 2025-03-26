from .create_command_block import *
from .migrate_command_block import *
from .parser import cli_parser
from .single_command_block import *

__all__ = ["run_cli"]


def run_cli():
    _ = cli_parser()
    args = _.parse_args()

    if args.command not in globals():
        _.print_help()
        return

    globals()[args.command](args)
