from datetime import datetime
import discord
import time
from botutils import BaseCog
from discord.ext import commands
import pytz

timezones = [
    "UTC",
    "America/New_York",
    "America/Chicago",
    "Australia/Brisbane",
    "Asia/Manila"
]


timezonesforhumans = [
    "UTC",
    "US Eastern",
    "US Central",
    "AEST",
    "Philippines"
]

fmt = '%Y-%m-%d %I:%M %p'
class BasicsCog(BaseCog):
    @commands.command()
    async def ping(self, ctx:commands.Context):
        m: discord.Message= await ctx.send("Pong...")
        responsetime = m.created_at - ctx.message.created_at
        responsetime = responsetime.total_seconds() * 1000
        before = time.monotonic()
        await ctx.trigger_typing()
        after = int((before - time.monotonic()) * 1000)
        embed = discord.Embed(title="Pong!", color=discord.Color(0xeb72a4))
        embed.add_field(name="bot.latency", value=f"{int(self.bot.latency * 1000)}ms")
        embed.add_field(name="Command Response Time", value=f"{int(responsetime)}ms")
        embed.add_field(name="Send Request Time", value=f"{after}ms")
        await m.edit(content=None, embed=embed)

    @commands.command()
    async def clock(self, ctx:commands.Context):
        embed = discord.Embed(title="Tick-tock!", color=discord.Color(0xeb72a4))
        now = datetime.utcnow()
        for tzstr, name in zip(timezones,timezonesforhumans):
            embed.add_field(name=name, value=pytz.utc.localize(now, is_dst=None).astimezone(pytz.timezone(tzstr)).strftime(fmt))
        embed.add_field(name='\u200b', value='\u200b')
        return await ctx.send(embed=embed)

    @commands.command()
    async def whosaround(self, ctx: commands.Context):
        embed = discord.Embed(title="Available Staff")
def setup(bot):
    bot.add_cog(BasicsCog(bot))
