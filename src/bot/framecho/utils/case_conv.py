import re

__all__ = ["camel_to_snake", "snake_to_camel"]


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def snake_to_camel(name: str) -> str:
    return "".join(x.title() for x in name.split("_"))
