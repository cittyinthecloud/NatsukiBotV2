import asyncio
import operator
import typing

import discord
from discord.ext import commands

EMOJIS_TO_IGNORE = [
    "\N{CROSS MARK}",
    "\N{WHITE HEAVY CHECK MARK}",
    "\N{MEMO}"
]


class ModeratorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context):
        if ctx.author.permissions_in(ctx.channel).manage_messages or (await ctx.bot.is_owner(ctx.author)):
            return True
        else:
            return False

    @commands.command()
    async def purge(self, ctx: commands.Context, count: int):
        await ctx.channel.delete_messages(await ctx.channel.history(limit=count + 1).flatten())

    @commands.command()
    async def say(self, ctx, *, thing):
        asyncio.create_task(ctx.message.delete())
        await ctx.send(thing)

    @commands.command(name="saychan", aliases=["saychannel", "sayin"])
    async def say_channel(self, ctx, channel: discord.TextChannel, *, thing):
        asyncio.create_task(ctx.message.delete())
        await channel.send(thing)

    @commands.command(name="sayyuri")
    async def say_yuri(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel], *, message):
        if not channel:
            channel = ctx.channel
        webhook: discord.Webhook = discord.utils.get(await ctx.guild.webhooks(), name="NatsukiBot")
        if not webhook:
            return await ctx.channel.send("I don't have a webhook :(")
        if webhook.channel != channel:
            try:
                await self._set_webhook_channel(webhook, channel)
            except discord.errors.Forbidden:
                return await ctx.channel.send("I don't have permission to move my webhook to that channel")

        await webhook.send(username="Yuri", avatar_url="https://i.imgur.com/4iUOu2Q.png", content=message)

    @commands.command()
    async def suggestion(self, ctx: commands.Context, index: int = 1):
        m: discord.Message = await ctx.send("Please wait, finding suggestion...")
        async with ctx.typing():
            suggestionsmessages = [x async for x in
                                   discord.utils.get(ctx.guild.channels, name="server_suggestions").history()
                                   if await self._is_incomplete_suggest(x)]

            def get_upvotes(x):
                reactions = discord.utils.get(x.reactions, emoji="\N{UPWARDS BLACK ARROW}")
                if not reactions:
                    return 0
                else:
                    return reactions.count

            sorted_x = sorted(zip(suggestionsmessages, map(get_upvotes, suggestionsmessages)),
                              key=operator.itemgetter(1), reverse=True)
            if not len(sorted_x):
                return await m.edit(content="No more suggestions")
            else:
                try:
                    theking: discord.Message = sorted_x[index - 1][0]
                    updoots = discord.utils.get(theking.reactions, emoji="\N{UPWARDS BLACK ARROW}").count
                    downdoots = discord.utils.get(theking.reactions, emoji="\N{DOWNWARDS BLACK ARROW}").count

                    embed = discord.Embed(
                        title=f"{updoots} \N{UPWARDS BLACK ARROW} | {downdoots} \N{DOWNWARDS BLACK ARROW}",
                        description=theking.content)
                    embed.set_footer(text=f"Written by {theking.author}", icon_url=theking.author.avatar_url)
                    return await m.edit(content="", embed=embed)
                except IndexError:
                    return await m.edit(content=f"No {index}th embed")

    async def _set_webhook_channel(self, webhook: discord.Webhook, channel: discord.TextChannel):
        return await self.bot.http.request(discord.http.Route('PATCH', '/webhooks/{webhook_id}', webhook_id=webhook.id),
                                           json={'channel_id': str(channel.id)})

    async def _is_incomplete_suggest(self, message: discord.Message):
        if not len(message.reactions):
            return False

        return not any(x.emoji in EMOJIS_TO_IGNORE for x in message.reactions)


def setup(bot):
    bot.add_cog(ModeratorCog(bot))
