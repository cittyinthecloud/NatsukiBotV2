import ast
import traceback

import discord
import requests
from discord.ext import commands


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class OwnerCog:
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

async def __local_check(self, ctx: commands.Context):
            if ctx.author.id == 84163178585391104 or (await ctx.bot.is_owner(ctx.author)):
                return True
            else:
                return False

    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    #@commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            #await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}\nTraceback: ```\n{traceback.print_tb(e.__traceback__)}')
            await ctx.send("```"+"".join(traceback.format_exception(type(e), e, e.__traceback__))+"```")
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    #@commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    #@commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        # noinspection PyBroadException
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send("```"+"".join(traceback.format_exception(type(e), e, e.__traceback__))+"```")
        else:
            await ctx.send(f'**`SUCCESS`** Reloaded {cog}')

    @commands.command(name='reloadall', hidden=True)
    #@commands.is_owner()
    async def cog_reloadall(self, ctx):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        extensions = list(self.bot.extensions.keys())
        # noinspection PyBroadException
        for cog in extensions:
            try:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            except Exception as e:
                await ctx.send("```" + "".join(traceback.format_exception(type(e), e, e.__traceback__)) + "```")
            else:
                await ctx.send(f'**`SUCCESS`** Reloaded {cog}')

    @commands.command(name="playing", hidden=True)
    #@commands.is_owner()
    async def pres_playing(self, ctx, *, content):
        await self.bot.change_presence(activity=discord.Game(content))

    @commands.command(name="eval")
    #@commands.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
          - `bot`: the bot instance
          - `discord`: the discord module
          - `commands`: the discord.ext.commands module
          - `ctx`: the invokation context
          - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))

        await ctx.send(result)

    @commands.command(name="ip")
    #@commands.is_owner()
    async def get_ip(self,ctx):
        await ctx.send(requests.get("https://api.ipify.org").text)

def setup(bot):
    bot.add_cog(OwnerCog(bot))
