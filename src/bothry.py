import discord
from discord.ext import commands
import json
import logging

def main():
    cogs = ["basic_cmds"]
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    logger = logging.getLogger(__name__)

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def setup_hook():
        for cog in cogs:
            await bot.load_extension(f"cogs.{cog}")
    
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, discord.ext.commands.CommandNotFound):
            logger.warning(f"CommandNotFound Exception: {error}")

    bot_token = ""

    with open("data.json") as f:
        bot_token = json.load(f)["bot_token"]

    bot.run(bot_token)


if __name__ == "__main__":
    main()
