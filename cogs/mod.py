import typing

from discord.ext import commands
import discord
import asyncio


class ModeratorCog:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context):
        print('cog local check')
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

    @commands.command(aliases=["saychan"])
    async def saychannel(self, ctx, channel: discord.TextChannel, *, thing):
        asyncio.create_task(ctx.message.delete())
        await channel.send(thing)

    @commands.command()
    async def sayyuri(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel], *, message):
        if not channel:
            channel = ctx.channel
        webhook: discord.Webhook = discord.utils.get(await ctx.guild.webhooks(), name="NatsukiBot")
        if not webhook:
            return await ctx.channel.send("I don't have a webhook :(")
        if webhook.channel != channel:
            try:
                await self.setwebhookchannel(webhook, channel)
            except discord.errors.Forbidden:
                return await ctx.channel.send("I don't have permission to move my webhook to that channel")

        await webhook.send(username="Yuri", avatar_url="https://i.imgur.com/4iUOu2Q.png", content=message)

    async def setwebhookchannel(self, webhook: discord.Webhook, channel: discord.TextChannel):
        return await self.bot.http.request(discord.http.Route('PATCH', '/webhooks/{webhook_id}', webhook_id=webhook.id),
                                           json={'channel_id': str(channel.id)})


def setup(bot):
    bot.add_cog(ModeratorCog(bot))
