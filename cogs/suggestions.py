import discord
from discord.ext import commands

vote_emoji = {
    "⬆": "⬇",
    "⬇": "⬆"
}


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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == 462824914769018882:
            return
        if payload.channel_id == 430396361045966860 and payload.emoji.name in vote_emoji:
            m: discord.Message = await self.bot.get_channel(430396361045966860).fetch_message(payload.message_id)
            # noinspection PyBroadException
            try:
                await m.remove_reaction(vote_emoji[payload.emoji.name], m.guild.get_member(payload.user_id))
            except Exception:
                pass


def setup(bot):
    bot.add_cog(EventCog(bot))
