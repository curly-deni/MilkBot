import datetime

import nextcord


class Paginator(nextcord.ui.View):
    def __init__(
        self,
        message,
        embed,
        author,
        bot,
        timeout,
        footerpage: bool = False,
        footerdatetime: bool = False,
        footerboticon: bool = False,
    ):
        super().__init__()
        self.footerpage = footerpage
        self.footerdatetime = footerdatetime
        self.footerboticon = footerboticon
        self.timeout = timeout
        self.message = message
        self.embeds = embed
        self.author = author
        self.bot = bot
        self.page = 0

        if self.footerpage:
            for embed in self.embeds:
                if not self.footerboticon:
                    embed.set_footer(
                        text=f"Страница: {self.embeds.index(embed) + 1} из {len(self.embeds)}"
                    )
                else:
                    embed.set_footer(
                        text=f"Страница: {self.embeds.index(embed) + 1} из {len(self.embeds)}",
                        icon_url=self.bot.user.avatar.url,
                    )

        if self.footerdatetime:
            for embed in self.embeds:
                if not self.footerboticon:
                    embed.timestamp = datetime.datetime.utcnow()
                else:
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(text="\u200b", icon_url=self.bot.user.avatar.url)

    async def start(self):
        await self.message.edit(
            embed=self.embeds[0],
            view=Paginator(
                self.message, self.embeds, self.author, self.bot, self.timeout
            ),
        )

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(embed=self.embeds[0], view=self)
        return await super().on_timeout()

    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.grey, disabled=True)
    async def previous(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        if self.author.id == interaction.user.id:
            self.page -= 1
            embed = self.embeds[self.page]
            if self.page == 0:
                button.disabled = True
            if self.page < len(self.embeds):
                self.next.disabled = False
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Вы не имеете право на это действие!", ephemeral=True
            )

    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.grey, disabled=False)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.author.id == interaction.user.id:
            self.page += 1
            embed = self.embeds[self.page]
            if self.page > 0:
                self.previous.disabled = False
            if self.page == len(self.embeds) - 1:
                button.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Вы не имеете право на это действие!", ephemeral=True
            )

    @nextcord.ui.button(emoji="❌", style=nextcord.ButtonStyle.red)
    async def delete(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        if self.author.id == interaction.user.id:
            await interaction.response.edit_message(view=None)
        else:
            await interaction.response.send_message(
                "Вы не имеете право на это действие!", ephemeral=True
            )
