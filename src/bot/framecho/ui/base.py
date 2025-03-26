from typing import Optional

from nextcord import User, Message, Interaction
from nextcord.ui import View

from framecho.logger import Logger

__all__ = ["BaseView"]


class BaseView(View):

    def __init__(
        self,
        user: User,
        *,
        private: bool = True,
        timeout: Optional[float] = 60,
        auto_defer: bool = False
    ):
        super().__init__(timeout=timeout, auto_defer=auto_defer)

        self._user = user
        self.message: Optional[Message] = None
        self._private = private

    @property
    def user(self):
        return self._user

    @property
    def private(self):
        return self._private

    async def start(self):
        if self.message is not None:
            await self._on_start()
            await self.message.edit(view=self)

    async def _on_start(self):
        pass

    async def interaction_check(self, interaction: Interaction):
        if interaction.user != self._user and self.private:
            return await interaction.send(
                "You are not allowed to use this view",
                # TODO добавить локализацию
                ephemeral=True,
                delete_after=15,
            )

        if not self.auto_defer:
            await interaction.response.defer(with_message=False)

        return await self.callback(interaction)

    async def callback(self, interaction: Interaction):
        raise NotImplementedError

    async def on_timeout(self) -> None:
        if self.message is not None:
            for child in self.children:
                try:
                    child.disabled = True
                except AttributeError:
                    continue
            try:
                if self.message:
                    await self.message.edit(view=self)
            except Exception as e:
                Logger().error("Error while updating view on timeout", e)

        self.stop()
