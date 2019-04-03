import typing

import discord
from discord import Role, Member
from discord.ext import commands
from discord.ext.commands import Context
from sqlitedict import SqliteDict

from utils.bot import BaseCog

allowed_role_ids = [
    376697695613485066,
    382402008553881600,
    391808780423397377,
    486115223720165386,
    382078965281718272,
    378965578553098242,
    495944125124968469,
    376696109973635096,
    393590602614308864,
    440693341735092266,
]

artists = [
    382402008553881600,
    391808780423397377,
    486115223720165386,
    382078965281718272,
]


class RoleCog(BaseCog):

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        with SqliteDict('./roledb.sqlite', autocommit=True) as roledb:
            roledb[str(member.id)] = list(map(lambda x: x.id, list(member.roles)))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        with SqliteDict('./roledb.sqlite', autocommit=True) as roledb:
            if str(member.id) in roledb:
                await member.add_roles(*list(

                    filter(lambda x: self.utils.is_assignable(x),
                           map(lambda x: member.guild.get_role(x),
                               roledb[str(member.id)]
                               )
                           )
                )
                                       )

    @commands.command(name="comedy-dark")
    async def comedy_dark(self, ctx):
        await self.iam.callback(self, ctx, role=self.bot.get_guild(339272843327963136).get_role(393590602614308864))

    @commands.command(aliases=["Iam", "IAM"])
    async def iam(self, ctx: Context, *, role: typing.Union[Role, str]):
        artist = self.bot.get_guild(339272843327963136).get_role(376696109973635096)

        if isinstance(role, str):
            rolea = discord.utils.find(lambda x: x.name.lower() == role.lower(), ctx.guild.roles)
            if rolea is None:
                return await ctx.send(f"Role {role} not found.")
            role = rolea

        if role.id not in allowed_role_ids:
            return await ctx.send("This role is not self-assignable. If it should be, please contact a staff member. "
                                  "If not, stop trying to do things you shouldn't, meanie!")
        member: Member = ctx.author
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"Removed {role.name}")
        else:
            if role.id in artists and artist not in member.roles:
                await member.add_roles(artist, reason="AutoAssignArtist")
            await member.add_roles(role, reason="Self Assign")
            await ctx.send(f"Added {role.name}")


def setup(bot):
    bot.add_cog(RoleCog(bot))
