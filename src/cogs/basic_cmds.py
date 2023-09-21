from discord.ext import commands
import datetime
import fflogs
import json
import utils
from hashlib import sha256
from ff_user import User
import calendar
import bot_backend

USERS_PATH = "./users.json"

class Bothry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = {}
        with open(USERS_PATH, "r") as f:
            loaded_user_data = json.load(f)
            for disc_id, user_data in loaded_user_data.items():
                disc_id = int(disc_id)
                self.users[disc_id] = User.from_dict(disc_id, user_data)


    @commands.command()
    async def register(self, ctx, lodestone_str: str=""):
        if not lodestone_str:
                bio_code = "bothry-" + str(
                    sha256(str(ctx.message.author.id).encode('utf-8')).hexdigest())
                await ctx.send(
                    "Input your character's lodestone URL to register. The first "
                    "character you register will be your primary character. Everything"
                    " else will be registered as an alt. To swap primary characters, "
                    "run `!register <lodesetone_url> primary`.\nYour lodestone code is"
                    f" `{bio_code}`")
                return

        else:
            bot_backend.register(ctx.message.author.id, lodestone_str, self.users)


        # @register.error
        # async def register_error(ctx, e):
        #     await ctx.send("The register command follows the following syntax: "
        #                    f"`!register <lodestone_url>`. Got an error: {e}")

    @commands.command()
    async def latest(self, ctx, fightname=None, analysis=""):
        uid, username = utils.get_id(ctx)

        fight = {}
        actual_name = fightname

        if fightname is None:
            for fight_name, encounter_id in utils.ENCOUNTER_ID_DICT.items():
                try:
                    cur_fight = fflogs.get_latest_fight_report(uid, encounter_id)
                    if not fight or cur_fight["startTime"] > fight["startTime"]:
                        fight = cur_fight
                        actual_name = fight_name
                except KeyError:
                        continue
                    
        else:
            fight = fflogs.get_latest_fight_report(
                uid, utils.ENCOUNTER_ID_DICT[fightname.lower()])

        report = fight["report"]
        fight_url = utils.gen_report_url(report["code"], report["fightID"])

        start_time = datetime.datetime.fromtimestamp(fight['startTime']/1000.0)
        _, minutes, seconds = utils.ms_to_time(fight['duration'])

        start_time_str = (
            f"{calendar.month_abbr[start_time.month]} {start_time.day}, "
            f"{start_time.year}"
        )

        await ctx.send(f"URL: {fight_url}\n```Job: {fight['spec']}\n"
                       f"Encounter: {actual_name}\n"
                       f"Parse: {round(float(fight['rankPercent']))}%\n"
                       f"Duration: {minutes}:{seconds}\n"
                       f"Start time: {start_time_str}```")
        analysis = str(analysis)

        if analysis == "a" or analysis == "analysis":
            fighter_info = fflogs.get_fighter_info(
                report["code"], report["fightID"], username)
            if fighter_info:
                await ctx.send(utils.gen_xivanalysis_url(report["code"],
                               report["fightID"], int(fighter_info["sourceID"])))
            else:
                raise Exception(
                    f"Couldn't find fighter with name {username} in report "
                    f"{report['code']} with fight id {report['fightID']}")

    @commands.command()
    async def whoami(self, ctx):
        _, username = utils.get_id(ctx)
        await ctx.send(f"Hi {username} :hearts:")

async def setup(bot):
    await bot.add_cog(Bothry(bot))