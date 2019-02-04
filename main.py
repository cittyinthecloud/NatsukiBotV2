import logging
import sys
import traceback

from discord.ext import commands
from discord.ext.commands import Bot
from SECRET import token

initial_extensions = [
    "cogs.owner",
    "cogs.roles",
    "cogs.error",
    "cogs.events",
    "cogs.fun",
    "cogs.gulag",
    "cogs.basics",
    "cogs.mod",
    "cogs.antiraid"
]

logging.basicConfig(level=logging.INFO)

bot: Bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))

if __name__ == '__main__':
    for extension in initial_extensions:
        # noinspection PyBroadException
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

bot.run(token)