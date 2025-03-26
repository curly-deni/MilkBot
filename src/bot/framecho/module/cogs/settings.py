from sqlalchemy import select

from framecho.cog import Cog

from framecho.context.abstract_context import AbstractContext
from framecho.option import Option

from config import STANDARD_PREFIX
from framecho.module.models.guild_prefix import GuildPrefix


class Settings(Cog):

    @Cog.hybrid_command()
    async def prefix(
        self,
        ctx: AbstractContext,
        prefix: str = Option(
            "prefix",
            "prefix to call message commands",
            required=False,
            min_length=0,
            max_length=5,
        ),
    ):

        model_query = select(GuildPrefix).where(GuildPrefix.guild_id == ctx.guild.id)
        model_results = await ctx.db_session.execute(model_query)
        model = model_results.scalars().one_or_none()

        if prefix:
            if not model:
                model = GuildPrefix(guild_id=ctx.guild.id, prefix=prefix)
                ctx.db_session.add(model)
            else:
                model.prefix = prefix
            await ctx.db_session.commit()
            return await ctx.send(f"Prefix set to {model.prefix}")

        if model:
            await ctx.db_session.delete(model)
            await ctx.db_session.commit()
        await ctx.send(f"Prefix set to default {STANDARD_PREFIX}")


def setup(bot):
    bot.add_cog(Settings(bot))
