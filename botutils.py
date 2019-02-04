from discord.ext import commands


class BaseCog:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

def is_in_channel(channel_id):
    async def predicate(ctx: commands.Context):
        return ctx.channel and ctx.channel.id == channel_id
    return commands.check(predicate)