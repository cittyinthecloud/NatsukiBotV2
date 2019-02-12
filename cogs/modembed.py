import re

import aiohttp
import discord
from discord.ext import commands

import SECRET


class GameModCog:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def addmod(self, ctx: commands.Context, *, inputstring: str):
        await ctx.message.delete()

        await ctx.send(content=None, embed=await str_to_modembed(inputstring))

    @commands.command()
    async def editmod(self, ctx: commands.Context, modname: str, *, inputstring: str):
        self.bot.loop.create_task(ctx.message.delete())

        def predicate(m: discord.Message):
            if not len(m.embeds):
                return False
            embed: discord.Embed = m.embeds[0]
            if re.match(modname, embed.title):
                return True
            return False

        message: discord.Message = await ctx.channel.history().find(predicate)
        await message.edit(embed=await str_to_modembed(inputstring))


async def str_to_modembed(inputstring):
    split = [str.strip('\"') for str in inputstring.split(',')]

    embed = discord.Embed(title=split[1], color=discord.Color(add_embed_color(split[5], split[8])))
    # embed.set_image("https://via.placeholder.com/1000x1")
    embed.description = split[4]
    add_field_checked(embed, "Author", split[2])
    add_field_checked(embed, "Reddit Name", split[3])
    # add_field_checked(embed, "Status", split[5])
    footerstuff = []
    if split[6] != "":
        footerstuff.append(f"Version {split[6]}")
    if split[8] != "":
        footerstuff.append(f"{split[5]}: {split[8]}")
    elif split[5] != "":
        footerstuff.append(f"{split[5]}")

    if len(footerstuff):
        embed.set_footer(text=" | ".join(footerstuff))

    try:
        split[9] = split[9].replace(";", "\n")
    except IndexError:
        pass
    add_field_checked(embed, "Contributors Needed", split[9])
    async with aiohttp.ClientSession(headers={"Authorization":f"Bearer {SECRET.bitly_access_token}"}) as session:
        if split[10] != "":
            resp = await session.post("https://api-ssl.bitly.com/v4/shorten",json={"long_url": split[10]})
            json = await resp.json()
            add_field_checked(embed, "Reddit", json["link"])
        if split[7] != "":
            resp = await session.post("https://api-ssl.bitly.com/v4/shorten",json={"long_url": split[7]})
            json = await resp.json()
            add_field_checked(embed, "Download", json["link"])
    return embed


def add_field_checked(embed, name, value):
    if value != "":
        embed.add_field(name=name, value=value, inline=True)


def add_embed_color(status: str, versioninfo: str):
    if status == "Planning":
        return 0xd7342a
    elif status == "Developing":
        return 0xe67e22
    elif status == "Playable":
        if versioninfo == "Full Release":
            return 0x25c059
        else:
            return 0xffb800
    elif status == "" or versioninfo == "":
        return 0


def setup(bot):
    bot.add_cog(GameModCog(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog("GameModCog")
