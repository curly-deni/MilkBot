from typing import Union

import nextcord
from nextcord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_member_count(self, data) -> int:

        guild: nextcord.Guild = self.bot.get_guild(
            data.guild_id
        )  # get the guild object using parsed guild_id

        return guild.member_count  # return the member count to the client

    @ipc.server.route()
    async def guilds(self, data) -> list[int]:
        return [guild.id for guild in self.bot.guilds]

    @ipc.server.route()
    async def guild_info(self, data) -> dict:

        guild: nextcord.Guild = self.bot.get_guild(data.guild_id)
        guild_info: dict = {
            "id": guild.id,
            "name": guild.name,
            "description": guild.description,
            "default_role": guild.default_role.id,
            "member_count": guild.member_count,
            "icon": guild.icon.url if guild.icon else "",
        }
        return guild_info

    @ipc.server.route()
    async def guild_text_channels(self, data) -> dict:

        guild: nextcord.Guild = self.bot.get_guild(data.guild_id)
        guild_info: dict = {
            "id": guild.id,
            "text_channels": [
                {"id": channel.id, "name": channel.name}
                for channel in guild.text_channels
            ],
        }
        return guild_info

    # @app.route("/send_embed", methods=["POST"])
    # async def send_embed():
    #     if request.headers["Key"] != self.bot.settings["ipc_key"]:
    #         return "Access Denied"
    #     message = await request.json
    #     message_keys = list(message.keys())
    #     channel = self.bot.get_channel(message["channel_id"])
    #     if "message_id" in message_keys:
    #         message_sended = await channel.fetch_message(message["message_id"])
    #         message_exist = True
    #     else:
    #         message_exist = False
    #     if "embed" in message_keys:
    #         if message["embed"]:
    #             embed: nextcord.Embed = nextcord.Embed()
    #             embed_dict = message["embed"]
    #             embed_keys = list(embed_dict.keys())
    #             if "title" in embed_keys:
    #                 embed.title = embed_dict["title"]
    #             if "description" in embed_keys:
    #                 embed.description = embed_dict["description"]
    #             if "color" in embed_keys:
    #                 color = str(hex(embed_dict["color"]))
    #                 embed.colour = nextcord.Colour.from_rgb(
    #                     int(color[:1], 16), int(color[2:3], 16), int(color[4:5], 16)
    #                 )
    #             if "url" in embed_keys:
    #                 embed.url = embed_dict["url"]
    #             if "thumbnail" in embed_keys:
    #                 if "url" in embed_dict["thumbnail"]:
    #                     embed.set_thumbnail(url=embed_dict["thumbnail"]["url"])
    #             if "image" in embed_keys:
    #                 if "url" in embed_dict["image"]:
    #                     embed.set_image(url=embed_dict["image"]["url"])
    #             if "footer" in embed_keys:
    #                 if (
    #                         "text" in embed_dict["footer"]
    #                         and "icon_url" in embed_dict["footer"]
    #                 ):
    #                     embed.set_footer(
    #                         text=embed_dict["footer"]["text"],
    #                         icon_url=embed_dict["footer"]["icon_url"],
    #                     )
    #                 elif "text" in embed_dict["footer"]:
    #                     embed.set_footer(text=embed_dict["footer"]["text"])
    #                 elif "icon_url" in embed_dict["footer"]:
    #                     embed.set_footer(icon_url=embed_dict["footer"]["icon_url"])
    #             if "fields" in embed_keys:
    #                 for field in embed_dict["fields"]:
    #                     if (
    #                             "name" in field.keys()
    #                             and "value" in field.keys()
    #                             and "inline" in field.keys()
    #                     ):
    #                         embed.add_field(
    #                             name=field["name"],
    #                             value=field["value"],
    #                             inline=field["inline"],
    #                         )
    #                     elif "name" in field.keys() and "value" in field.keys():
    #                         embed.add_field(
    #                             name=field["name"], value=field["value"]
    #                         )
    #                     elif "value" in field.keys():
    #                         embed.add_field(name="\u200b", value=field["value"])
    #             if "content" in message_keys:
    #                 if message_exist:
    #                     await message_sended.edit(message["content"], embed=embed)
    #                 else:
    #                     message_sended = await channel.send(
    #                         message["content"], embed=embed
    #                     )
    #             else:
    #                 if message_exist:
    #                     await message_sended.edit(embed=embed)
    #                 else:
    #                     message_sended = await channel.send(embed=embed)
    #     elif "content" in message_keys:
    #         if message_exist:
    #             await message_sended.edit(message["content"])
    #         else:
    #             message_sended = await channel.send(message["content"])
    #
    #     if not message_sended:
    #         try:
    #             self.bot.database.session.add(
    #                 Embeds(
    #                     id=message_sended.id,
    #                     guild_id=channel.guild.id,
    #                     channel_id=channel.id,
    #                     json=json.dumps(message),
    #                 )
    #             )
    #             self.bot.database.session.commit()
    #         except Exception as ex:
    #             print(ex)
    #     else:
    #         try:
    #             ms = self.bot.database.session.query(Embeds).get(
    #                 [message_sended.id, channel.id]
    #             )
    #             ms.json = json.dumps(message)
    #             self.bot.database.session.commit()
    #         except Exception as ex:
    #             print(ex)
    #
    #     return "200"

    @ipc.server.route()
    async def guild_voice_channels(self, data) -> dict:

        guild: nextcord.Guild = self.bot.get_guild(data.guild_id)
        guild_info = {
            "id": guild.id,
            "voice_channels": [
                {"id": channel.id, "name": channel.name}
                for channel in guild.voice_channels
            ],
        }
        return guild_info

    @ipc.server.route()
    async def member_info(self, data) -> Union[dict, str]:

        guild = self.bot.get_guild(data.guild_id)

        try:
            member = guild.get_member(data.member_id)
        except:
            return "Invalid Data"

        member_data = {
            "id": member.id,
            "name": member.name,
            "display_name": member.display_name,
            "roles": [{"id": role.id, "name": role.name} for role in member.roles],
            "avatar": member.avatar.url
            if member.avatar
            else f"https://cdn.discordapp.com/embed/avatars/{str(int(member.discriminator) % 5)}.png",
        }
        return member_data


def setup(bot):
    bot.add_cog(IpcRoutes(bot))
