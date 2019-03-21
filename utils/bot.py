import discord
from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = BotUtils(self.bot)


class BotUtils:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def is_assignable(self, role: discord.Role):
        if role.is_default():
            return False
        return role.guild.get_member(self.bot.user.id).top_role > role

    def get_assignable_roles(self, guild: discord.Guild):
        if not guild.me.guild_permissions.manage_roles:
            return iter(())
        else:
            return filter(self.is_assignable, guild.roles)


def is_in_channel(channel_id):
    async def predicate(ctx: commands.Context):
        return ctx.channel and ctx.channel.id == channel_id

    return commands.check(predicate)
