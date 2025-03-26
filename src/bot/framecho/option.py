from inspect import Parameter
from typing import Any, Optional, Union

import nextcord.utils
from nextcord import ChannelType, SlashOption


class Option:
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = False,
        *,
        type: Any = None,  # noqa
        name_localizations: dict = None,
        description_localizations: dict = None,
        choices: dict = None,
        choice_localizations: dict = None,
        channel_types: list[ChannelType] = None,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        min_length: int = None,
        max_length: int = None,
        default: Any = None,
        verify=True
    ):
        self.name = name
        self.description = description
        self.required = required
        self.name_localizations = name_localizations
        self.description_localizations = description_localizations
        self.choices = choices
        self.choice_localizations = choice_localizations
        self.channel_types = channel_types
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.default = default
        self.verify = verify
        self.type = type

        self.param_name = (None,)
        self.kind = None

    def load(self, *, name: str, type=None, kind=None):  # noqa
        self.param_name = name

        if self.type is None:
            self.type = type

        self.kind = kind

    @property
    def slash_option(self) -> dict:
        ret = {}
        if self.type:
            ret["annotation"] = self.type

        ret["default"] = SlashOption(
            name=self.name,
            description=self.description,
            required=self.required,
            name_localizations=self.name_localizations,
            description_localizations=self.description_localizations,
            choices=self.choices,
            choice_localizations=self.choice_localizations,
            channel_types=self.channel_types,
            min_value=self.min_value,
            max_value=self.max_value,
            min_length=self.min_length,
            max_length=self.max_length,
            default=(
                self.default if self.default is not None else nextcord.utils.MISSING
            ),
        )

        return ret

    @property
    def message_option(self):
        ret = {}
        if self.type:
            ret["annotation"] = self.type

        if self.default:
            ret["default"] = self.default
        elif self.required:
            ret["default"] = Parameter.empty
        else:
            ret["default"] = None

        return ret
