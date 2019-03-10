import asyncio
import re
import typing
from datetime import datetime, timedelta, timezone

import attr
import discord
from discord.ext import commands


@attr.s(auto_attribs=True)
class GulagState:
    ungulagtime: datetime
    roles: typing.List[int]
    guild: int
    reason: str


def to_seconds(timestr):
    seconds = 0
    for part in timestr.split(':'):
        seconds = seconds * 60 + int(part)
    return seconds


class GulagCog:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.gulagchecker())
        self.gulags = {}
        self.gulagrole = None

    async def __local_check(self, ctx: commands.Context):
        if await ctx.bot.is_owner(ctx.author):
            return True
        else:
            return ctx.author.guild_permissions.kick_members

    @staticmethod
    def parsetimestr(timestr: str) -> int:
        timeunits = re.findall(r"\d+[smhdw]", timestr)
        totaltime = 0
        for unit in timeunits:
            temp = int(unit[:-1])
            if unit[-1] == "m":
                temp = temp * 60
            elif unit[-1] == "h":
                temp = temp * 60 * 60
            elif unit[-1] == "d":
                temp = temp * 60 * 60 * 24
            elif unit[-1] == "w":
                temp = temp * 60 * 60 * 24 * 7
            totaltime += temp
        return totaltime

    @commands.command(hidden=True)
    async def timeparsetest(self, ctx, timestr):
        return await ctx.send(f'{self.parsetimestr(timestr)} seconds')

    async def addGulag(self, member: discord.Member, time: int, gulager: str, reason: str):
        now = datetime.now(timezone.utc)
        ungulag_time = now + timedelta(seconds=time)
        roles = list(map(lambda x: x.id, member.roles))[1:]
        self.gulags[member.id] = GulagState(ungulagtime=ungulag_time, roles=roles, guild=member.guild.id,
                                            reason=reason)
        roles = member.roles[1:]
        await member.add_roles(self.gulagrole, reason=f"Gulaged by {gulager}")
        await member.remove_roles(*roles, reason=f"Gulaged by {gulager}")

    @commands.command()
    async def gulag(self, ctx: commands.Context, member: discord.Member, time: str, *, reason: str):
        if not re.match(r"\d+[smhdw]", time):
            return await ctx.send("That's not a valid time string. Example: 1h4m30s")
        else:
            await self.addGulag(member, self.parsetimestr(time), ctx.author, )
            await ctx.send(f"{ctx.author.mention} gulaged {member}")

    @commands.command()
    async def ungulag(self, ctx, member: discord.Member):
        gulagstate: GulagState = self.gulags.pop(member.id, None)
        if not gulagstate:
            return await ctx.send("User is not gulaged.")
        guild: discord.Guild = self.bot.get_guild(gulagstate.guild)
        roles: typing.List[discord.Role] = list(map(guild.get_role, gulagstate.roles))
        print(roles)
        await member.remove_roles(self.gulagrole, reason=f"Ungulaged by {ctx.author}.")
        await member.add_roles(*roles, reason=f"Ungulaged by {ctx.author}.")
        await ctx.send(f"{ctx.author.mention} ungulaged {member.mention}")

    async def gulagchecker(self):
        await self.bot.wait_until_ready()
        self.gulagrole = discord.utils.get(self.bot.guilds[0].roles, name="Probationary")
        while True:
            await self.gulag_check()
            await asyncio.sleep(5)

    async def gulag_check(self):
        toRemove = []
        for memberid in self.gulags:
            if datetime.now(timezone.utc) > self.gulags[memberid].ungulagtime:
                guild: discord.Guild = self.bot.get_guild(self.gulags[memberid].guild)
                if not guild.get_member(memberid):
                    continue
                else:
                    gulagstate: GulagState = self.gulags[memberid]
                    toRemove.append(memberid)
                    member: discord.Member = guild.get_member(memberid)
                    roles: typing.List[discord.Role] = list(map(guild.get_role, gulagstate.roles))
                    print(roles)
                    await member.remove_roles(self.gulagrole, reason=f"Ungulaged by timer.")
                    await member.add_roles(*roles, reason=f"Ungulaged by timer.")

                    async def ungulagmessage():
                        try:
                            await member.send("You have been ungulaged. Don't do it again meanie!")
                        except discord.Forbidden:
                            pass

                    asyncio.create_task(ungulagmessage())

        for x in toRemove:
            self.gulags.pop(x)


def setup(bot):
    bot.add_cog(GulagCog(bot))
