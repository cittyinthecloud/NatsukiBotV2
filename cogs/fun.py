import random

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

import msweeper
from botutils import is_in_channel


class FunCog:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, float(15), BucketType.member)
    async def bulli(self, ctx: commands.Context):
        if ctx.channel.id == 339272843327963136:
            return
        await ctx.send("No bulli!", file=discord.File(f"images/nobulli{random.randint(0,11)}.png", "nobulli.png"))

    @commands.command()
    @commands.cooldown(1, float(10), BucketType.member)
    @is_in_channel(373669334993600523)
    async def minesweeper(self, ctx: commands.Context, sizex: int, sizey: int, bombcount: int):
        if sizex > 14 or sizey > 14 or bombcount > (sizex * sizey):
            return await ctx.send("You made the board too big, baka!")
        await ctx.send(f'\N{BOMB} x {bombcount} \n{msweeper.generate_board(sizex, sizey, bombcount)}')


def setup(bot):
    bot.add_cog(FunCog(bot))
