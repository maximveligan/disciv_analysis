import discord
from discord.ext import commands
import json

def main():
    cogs = ["basic_cmds"]
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def setup_hook():
        for cog in cogs:
            await bot.load_extension(f"cogs.{cog}")

    bot_token = ""

    with open("data.json") as f:
        bot_token = json.load(f)["bot_token"]

    bot.run(bot_token)


if __name__ == "__main__":
    main()
