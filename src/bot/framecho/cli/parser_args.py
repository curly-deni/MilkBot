import argparse

__all__ = [
    "add_module_param",
    "add_name_param",
    "add_type_param",
    "add_id_or_head_param",
    "add_id_param",
]


def add_module_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-m", "--module", help="The name of the module used.", default="app"
    )
    return parser


def add_name_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-n", "--name", help="The name of the component.", required=True
    )
    return parser


def add_type_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-t",
        "--type",
        choices=["folder", "file"],
        help="The type of the component.",
        required=True,
    )
    return parser


def add_id_or_head_param(parser: argparse.ArgumentParser):
    parser.add_argument("-i", "--id", help="The ID of the component.", default="head")
    return parser


def add_id_param(parser: argparse.ArgumentParser):
    parser.add_argument("-i", "--id", help="The ID of the component.", required=True)
    return parser
