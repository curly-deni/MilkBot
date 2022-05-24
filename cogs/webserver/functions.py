# for discord
import nextcord
import os
from nextcord.ext import commands, tasks
from quart import Quart, request
import json
from database import Embeds

import logging

app = Quart(__name__)


class WebServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @app.route("/")
        async def welcome():
            return f"Hello World, this is Webserver for {self.bot.user.name}."

        @app.route("/guilds")
        async def guilds():
            if request.headers["Key"] != self.bot.settings["ipc_key"]:
                return "Access Denied"
            return {guild.id for guild in self.bot.guilds}

        @app.route("/guild_info")
        async def guild_info():
            if request.headers["Key"] != self.bot.settings["ipc_key"]:
                return "Access Denied"
            if request.args["guild_id"]:
                try:
                    guild_id = int(request.args["guild_id"])
                except:
                    return "Invalid guild id"
            else:
                return "Invalid guild id"

            guild: nextcord.Guild = self.bot.get_guild(guild_id)
            guild_info = {
                "id": guild.id,
                "name": guild.name,
                "description": guild.description,
                "default_role": guild.default_role.id,
                "member_count": guild.member_count,
                "icon": guild.icon.url if guild.icon else "",
            }
            return json.dumps(guild_info)

        @app.route("/guild_text_channels")
        async def guild_text_channels():
            if request.headers["Key"] != self.bot.settings["ipc_key"]:
                return "Access Denied"
            if request.args["guild_id"]:
                try:
                    guild_id = int(request.args["guild_id"])
                except:
                    return "Invalid guild id"
            else:
                return "Invalid guild id"

            guild: nextcord.Guild = self.bot.get_guild(guild_id)
            guild_info = {
                "id": guild.id,
                "text_channels": [
                    {"id": channel.id, "name": channel.name}
                    for channel in guild.text_channels
                ],
            }
            return json.dumps(guild_info)

        @app.route("/send_embed", methods=["POST"])
        async def send_embed():
            if request.headers["Key"] != self.bot.settings["ipc_key"]:
                return "Access Denied"
            message = await request.json
            message_keys = list(message.keys())
            channel = self.bot.get_channel(message["channel_id"])
            if "message_id" in message_keys:
                message_sended = await channel.fetch_message(message["message_id"])
                message_exist = True
            else:
                message_exist = False
            if "embed" in message_keys:
                if message["embed"]:
                    embed: nextcord.Embed = nextcord.Embed()
                    embed_dict = message["embed"]
                    embed_keys = list(embed_dict.keys())
                    if "title" in embed_keys:
                        embed.title = embed_dict["title"]
                    if "description" in embed_keys:
                        embed.description = embed_dict["description"]
                    if "color" in embed_keys:
                        color = str(hex(embed_dict["color"]))
                        embed.colour = nextcord.Colour.from_rgb(
                            int(color[:1], 16), int(color[2:3], 16), int(color[4:5], 16)
                        )
                    if "url" in embed_keys:
                        embed.url = embed_dict["url"]
                    if "thumbnail" in embed_keys:
                        if "url" in embed_dict["thumbnail"]:
                            embed.set_thumbnail(url=embed_dict["thumbnail"]["url"])
                    if "image" in embed_keys:
                        if "url" in embed_dict["image"]:
                            embed.set_image(url=embed_dict["image"]["url"])
                    if "footer" in embed_keys:
                        if (
                            "text" in embed_dict["footer"]
                            and "icon_url" in embed_dict["footer"]
                        ):
                            embed.set_footer(
                                text=embed_dict["footer"]["text"],
                                icon_url=embed_dict["footer"]["icon_url"],
                            )
                        elif "text" in embed_dict["footer"]:
                            embed.set_footer(text=embed_dict["footer"]["text"])
                        elif "icon_url" in embed_dict["footer"]:
                            embed.set_footer(icon_url=embed_dict["footer"]["icon_url"])
                    if "fields" in embed_keys:
                        for field in embed_dict["fields"]:
                            if (
                                "name" in field.keys()
                                and "value" in field.keys()
                                and "inline" in field.keys()
                            ):
                                embed.add_field(
                                    name=field["name"],
                                    value=field["value"],
                                    inline=field["inline"],
                                )
                            elif "name" in field.keys() and "value" in field.keys():
                                embed.add_field(
                                    name=field["name"], value=field["value"]
                                )
                            elif "value" in field.keys():
                                embed.add_field(name="\u200b", value=field["value"])
                    if "content" in message_keys:
                        if message_exist:
                            await message_sended.edit(message["content"], embed=embed)
                        else:
                            message_sended = await channel.send(
                                message["content"], embed=embed
                            )
                    else:
                        if message_exist:
                            await message_sended.edit(embed=embed)
                        else:
                            message_sended = await channel.send(embed=embed)
            elif "content" in message_keys:
                if message_exist:
                    await message_sended.edit(message["content"])
                else:
                    message_sended = await channel.send(message["content"])

            if not message_sended:
                try:
                    self.bot.database.session.add(
                        Embeds(
                            id=message_sended.id,
                            guild_id=channel.guild.id,
                            channel_id=channel.id,
                            json=json.dumps(message),
                        )
                    )
                    self.bot.database.session.commit()
                except Exception as ex:
                    print(ex)
            else:
                try:
                    ms = self.bot.database.session.query(Embeds).get(
                        [message_sended.id, channel.id]
                    )
                    ms.json = json.dumps(message)
                    self.bot.database.session.commit()
                except Exception as ex:
                    print(ex)

            return "200"

        @app.route("/guild_voice_channels")
        async def guild_voice_channels():
            if request.headers["Key"] != self.bot.settings["ipc_key"]:
                return "Access Denied"
            if request.args["guild_id"]:
                try:
                    guild_id = int(request.args["guild_id"])
                except:
                    return "Invalid guild id"
            else:
                return "Invalid guild id"

            guild: nextcord.Guild = self.bot.get_guild(guild_id)
            guild_info = {
                "id": guild.id,
                "voice_channels": [
                    {"id": channel.id, "name": channel.name}
                    for channel in guild.voice_channels
                ],
            }
            return json.dumps(guild_info)

        @app.route("/member_info")
        async def member_info():
            if request.headers["Key"] != self.bot.settings["ipc_key"]:
                return "Access Denied"
            guild_id = request.args["guild_id"]
            member_id = request.args["member_id"]

            try:
                guild_id = int(guild_id)
                member_id = int(member_id)
            except:
                return "Invalid Data"

            guild = self.bot.get_guild(guild_id)

            try:
                member = guild.get_member(member_id)
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
            return json.dumps(member_data)

        self.cog_load()

    def cog_load(self):
        self.web_server = self.bot.loop.create_task(
            app.run_task("0.0.0.0", port=os.environ.get("PORT", 6368))
        )

    async def cog_unload(self):
        self.web_server.cancel()

    @tasks.loop()
    async def web_server(self):
        app.run(host="0.0.0.0", port=6368)

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    log = logging.getLogger("werkzeug")
    # log.disabled = True
    bot.add_cog(WebServer(bot))
