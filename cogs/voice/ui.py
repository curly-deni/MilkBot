import nextcord


class ChannelModal(nextcord.ui.Modal):
    def __init__(self, title=None, label=None, placeholder=None):
        super().__init__(title=title, timeout=60.0)

        self.field = nextcord.ui.TextInput(
            label=label, placeholder=placeholder, required=True
        )
        self.add_item(self.field)

    async def callback(self, interaction: nextcord.Interaction):
        self.stop()

    def value(self):
        return self.field.value


class ChannelSelector(nextcord.ui.View):
    def __init__(self, author, placeholder):
        super().__init__(timeout=60.0)

        options = []

        for member in author.voice.channel.members:
            options.append(
                nextcord.SelectOption(label=member.display_name, value=member.id)
            )

        options.append(nextcord.SelectOption(label="Свой вариант", value="0"))

        self.selector = nextcord.ui.Select(placeholder=placeholder, options=options)
        self.add_item(self.selector)

    async def interaction_check(self, interaction: nextcord.Interaction):
        self.value = int(self.selector.values[0])
        self.stop()
        return True
