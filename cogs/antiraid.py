import asyncio

import aiohttp
import bs4
import discord
from discord.ext import commands

from cogs.gulag import GulagCog


class RaidCog(commands.Cog):
    _session: aiohttp.ClientSession

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._gulag: GulagCog = bot.cogs["GulagCog"]
        self.pings = {}
        self.bot.loop.create_task(self.pingResetter())

    def __unload(self):
        self.bot.loop.create_task(self._session.close())

    async def on_message(self, message: discord.Message):
        if message.role_mentions and len(list(filter(lambda x: x.name != "Moderator", message.role_mentions))):
            self.pings[message.author.id] = self.pings.get(message.author.id, 0) + 1
            if self.pings[message.author.id] > 3:
                await self._gulag.add_gulag(message.author, 30 * 60, "NatsukiBot AntiRaid[TM]",
                                           "Pinged roles in more than 3 messages over 30 seconds")
                await message.channel.send(f"{message.author.mention} has been autogulaged for suspected raiding. If "
                                           f"this is in correct, please contact a staff member.")
        if message.attachments:
            attachment: discord.Attachment = message.attachments[0]
            async with self._session.get("https://iqdb.org/", params={"url": attachment.url}) as r:
                soup = bs4.BeautifulSoup(await r.text())
                match = soup.select("#pages")[0]("div")[1].table
                if match.tr.string == "Best match" and "Explicit" in match("tr")[3].string and \
                        int(match("tr")[4].string[:2]) > 90:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} NSFW Images are not allowed.")

    async def pingResetter(self):
        self._session = aiohttp.ClientSession()
        await self.bot.wait_until_ready()
        while True:
            self.pings = {}
            await asyncio.sleep(30)


def setup(bot):
    bot.add_cog(RaidCog(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog("RaidCog")
