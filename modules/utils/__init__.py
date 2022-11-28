import asyncio
import functools
from typing import Callable, Coroutine, TypeVar

import nextcord
from nextcord.ext import commands

T = TypeVar("T")


def make_async(func: Callable) -> Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def list_split(original_list) -> list[list]:
    return_list: list = []
    original_list_len_div_by_10: int = len(original_list) // 10
    for i in range(original_list_len_div_by_10 + 1):
        return_list.append(original_list[i * 10 : (i + 1) * 10])
    return return_list


def to_binary(a) -> list:
    l, m = [], []
    for i in a:
        l.append(ord(i))
    for i in l:
        m.append(int(bin(i)[2:]))
    return m


async def create_cancel_msg(
    self,
    ctx: commands.Context,
    name: str,
    on_cancel: Callable[[], T],
    on_message: Callable[[nextcord.Message], T],
) -> T:
    color_help = await ctx.send(name)
    await color_help.add_reaction("❌")

    async def get_reaction():
        def check(reaction: nextcord.Reaction, user: nextcord.User):
            return reaction.emoji in ["❌"] and user == ctx.message.author

        reaction, user = await self.bot.wait_for("reaction_add", check=check)
        return on_cancel()

    async def get_message() -> int:
        def check(message: nextcord.Message):
            return message.author == ctx.author and message.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check)
        color = on_message(msg)
        await msg.delete()
        return color

    tasks = [get_message(), get_reaction()]
    finished, unfinished = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED
    )

    result = finished.pop().result()
    for task in unfinished:
        task.cancel()
    await asyncio.wait(unfinished)
    await color_help.delete()
    return result


async def create_cancel_msg_without_ctx(
    bot,
    author: nextcord.Member,
    channel: nextcord.TextChannel,
    name: str,
    on_cancel: Callable[[], T],
    on_message: Callable[[nextcord.Message], T],
) -> T:
    color_help = await channel.send(name)
    await color_help.add_reaction("❌")

    async def get_reaction():
        def check(reaction: nextcord.Reaction, user: nextcord.User):
            return reaction.emoji in ["❌"] and user == author

        reaction, user = await bot.wait_for("reaction_add", check=check)
        return on_cancel()

    async def get_message() -> int:
        def check(message: nextcord.Message):
            return message.author == author and message.channel == channel

        msg = await bot.wait_for("message", check=check)
        color = on_message(msg)
        await msg.delete()
        return color

    tasks = [get_message(), get_reaction()]
    finished, unfinished = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED
    )

    result = finished.pop().result()
    for task in unfinished:
        task.cancel()
    await asyncio.wait(unfinished)
    await color_help.delete()
    return result
