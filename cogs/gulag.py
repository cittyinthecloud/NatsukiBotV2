import asyncio
import re
import typing
from datetime import datetime, timedelta, timezone

import attr
import discord
from discord.ext import commands
from sqlitedict import SqliteDict


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


async def can_gulag(ctx):
    if await ctx.bot.is_owner(ctx.author):
        return True
    else:
        return ctx.author.guild_permissions.kick_members


def can_gulag_check():
    return commands.check(can_gulag)


class GulagCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gulags = {}
        self.gulag_role = None
        self.bot.loop.create_task(self.gulagchecker())

    @staticmethod
    def parse_time_string(timestr: str) -> int:
        time_units = re.findall(r"\d+[smhdw]", timestr)
        total_time = 0
        for unit in time_units:
            temp = int(unit[:-1])
            if unit[-1] == "m":
                temp = temp * 60
            elif unit[-1] == "h":
                temp = temp * 60 * 60
            elif unit[-1] == "d":
                temp = temp * 60 * 60 * 24
            elif unit[-1] == "w":
                temp = temp * 60 * 60 * 24 * 7
            total_time += temp
        return total_time

    @commands.command(hidden=True)
    async def timeparsetest(self, ctx, timestr):
        return await ctx.send(f'{self.parse_time_string(timestr)} seconds')

    async def add_gulag(self, member: discord.Member, time: int, gulager: str, reason: str):
        now = datetime.now(timezone.utc)
        ungulag_time = now + timedelta(seconds=time)
        roles = list(map(lambda x: x.id, member.roles))[1:]
        self.gulags[member.id] = GulagState(ungulagtime=ungulag_time, roles=roles, guild=member.guild.id,
                                            reason=reason)
        roles = member.roles[1:]
        await member.add_roles(self.gulag_role, reason=f"Gulaged by {gulager}")
        await member.remove_roles(*roles, reason=f"Gulaged by {gulager}")

    @commands.command()
    @can_gulag_check()
    async def gulag(self, ctx: commands.Context, member: discord.Member, time: str, *, reason: str):
        if not re.match(r"\d+[smhdw]", time):
            return await ctx.send("That's not a valid time string. Example: 1h4m30s")
        else:
            await self.add_gulag(member, self.parse_time_string(time), ctx.author, reason)
            await ctx.send(f"{ctx.author.mention} gulaged {member}")
            with SqliteDict('./gulags.sqlite', autocommit=True) as gulagdb:
                gulagdb[str(member.id)] = gulagdb.get(str(member.id), 0) + 1
                if gulagdb[str(member.id)] > 3:
                    await ctx.author.send(f"{member} has been gulaged more than 3 times.")

    @commands.command()
    @can_gulag_check()
    async def ungulag(self, ctx, member: discord.Member):
        gulag_state: GulagState = self.gulags.pop(member.id, None)
        if not gulag_state:
            return await ctx.send("User is not gulaged.")
        guild: discord.Guild = self.bot.get_guild(gulag_state.guild)
        roles: typing.List[discord.Role] = list(map(guild.get_role, gulag_state.roles))
        print(roles)
        await member.remove_roles(self.gulag_role, reason=f"Ungulaged by {ctx.author}.")
        await member.add_roles(*roles, reason=f"Ungulaged by {ctx.author}.")
        await ctx.send(f"{ctx.author.mention} ungulaged {member.mention}")

    async def gulagchecker(self):
        await self.bot.wait_until_ready()
        self.gulag_role = discord.utils.get(self.bot.guilds[0].roles, name="Probationary")
        while True:
            await self.gulag_check()
            await asyncio.sleep(5)

    async def gulag_check(self):
        to_remove = []
        for member_id in self.gulags:
            if datetime.now(timezone.utc) > self.gulags[member_id].ungulagtime:
                guild: discord.Guild = self.bot.get_guild(self.gulags[member_id].guild)
                if not guild.get_member(member_id):
                    continue
                else:
                    gulag_state: GulagState = self.gulags[member_id]
                    to_remove.append(member_id)
                    member: discord.Member = guild.get_member(member_id)
                    roles: typing.List[discord.Role] = list(map(guild.get_role, gulag_state.roles))
                    print(roles)
                    await member.remove_roles(self.gulag_role, reason=f"Ungulaged by timer.")
                    await member.add_roles(*roles, reason=f"Ungulaged by timer.")

                    async def ungulag_message():
                        try:
                            await member.send("You have been ungulaged. Don't do it again meanie!")
                        except discord.Forbidden:
                            pass

                    asyncio.create_task(ungulag_message())

        for x in to_remove:
            self.gulags.pop(x)

    @commands.group(name="gulagcount", invoke_without_command=True)
    async def gulag_count_default(self, ctx: commands.Context):
        with SqliteDict('./gulags.sqlite', autocommit=True) as gulagdb:
            if not str(ctx.author.id) in gulagdb:
                gulagdb[str(ctx.author.id)] = 0
            await ctx.send(
                f"{ctx.author.mention} has been gulaged {gulagdb[str(ctx.author.id)]}" +
                f" time{'s' if gulagdb[str(ctx.author.id)] != 1 else ''}")

    @gulag_count_default.command(name="add", aliases=["inc"])
    @can_gulag_check()
    async def gulag_count_add(self, ctx: commands.Context, member: discord.User, amount: typing.Optional[int] = 1):
        with SqliteDict('./gulags.sqlite', autocommit=True) as gulagdb:
            gulagdb[str(member.id)] = gulagdb.get(str(member.id), 0) + amount
            await ctx.send(f"Incremented {member.mention}'s gulag count to {gulagdb[str(member.id)]}")

    @gulag_count_default.command(name="sub", aliases=["dec"])
    @can_gulag_check()
    async def gulag_count_sub(self, ctx: commands.Context, member: discord.User, amount: typing.Optional[int] = 1):
        with SqliteDict('./gulags.sqlite', autocommit=True) as gulagdb:
            gulagdb[str(member.id)] = gulagdb.get(str(member.id), 0) - amount
            await ctx.send(f"Decremented {member.mention}'s gulag count to {gulagdb[str(member.id)]}")

    @gulag_count_default.command(name="set")
    @can_gulag_check()
    async def gulag_count_set(self, ctx: commands.Context, member: discord.User, amount: typing.Optional[int] = 0):
        with SqliteDict('./gulags.sqlite', autocommit=True) as gulagdb:
            gulagdb[str(member.id)] = amount
            await ctx.send(f"Set {member.mention}'s gulag count to {amount}")

    @gulag_count_default.command(name="check", aliases=["for"])
    @can_gulag_check()
    async def gulag_count_check(self, ctx: commands.Context, member: discord.User):
        with SqliteDict('./gulags.sqlite', autocommit=True) as gulagdb:
            if not str(member.id) in gulagdb:
                gulagdb[str(member.id)] = 0
            await ctx.send(
                f"{member.mention} has been gulaged {gulagdb[str(member.id)]}" +
                f" time{'s' if gulagdb[str(member.id)] != 1 else ''}")


def setup(bot):
    bot.add_cog(GulagCog(bot))


def teardown(bot):
    bot.remove_cog("GulagCog")
