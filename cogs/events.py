import discord
from discord.ext import commands


class EventCog:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        # if "bulli" in message.clean_content.lower() and not message.author.bot:
        #     message.channel: discord.TextChannel
        #     await message.channel.send("No bulli!", file=discord.File("images/nobulli0.png", "nobulli0.png"))
        if message.channel.id == 430396361045966860:
            message.author: discord.Member
            if message.author.permissions_in(message.channel).manage_messages and "$" in message.clean_content:
                return
            await message.add_reaction("⬆")
            await message.add_reaction("⬇")
        # await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(EventCog(bot))
