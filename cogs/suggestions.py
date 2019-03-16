import discord
from discord.ext import commands


class EventCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == 430396361045966860:
            message.author: discord.Member
            if message.author.permissions_in(message.channel).manage_messages and "$" in message.clean_content:
                return
            await message.add_reaction("⬆")
            await message.add_reaction("⬇")

def setup(bot):
    bot.add_cog(EventCog(bot))
