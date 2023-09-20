import discord
from discord.ext import commands
import datetime
import fflogs
import json
import utils
from hashlib import sha256
from ff_user import User
import typing
import calendar

intents = discord.Intents.default()
intents.message_content = True

bot_token = ""

with open("data.json") as f:
    bot_token = json.load(f)["bot_token"]

bot = commands.Bot(command_prefix='!', intents=intents)

users_path = "./users.json"
users: typing.Dict[int, User] = {}

with open(users_path, "r") as f:
    loaded_user_data = json.load(f)
    for disc_id, user_data in loaded_user_data.items():
        disc_id = int(disc_id)
        users[disc_id] = User.from_dict(disc_id, user_data)


@bot.command()
async def register(ctx, lodestone_str: str=""):
    if not lodestone_str:
        bio_code = "bothry-" + str(
            sha256(str(ctx.message.author.id).encode('utf-8')).hexdigest())
        print(str(ctx.message.author.id))
        await ctx.send(
            "Input your character's lodestone URL to register. The first "
            "character you register will be your primary character. Everything"
            " else will be registered as an alt. To swap primary characters, "
            "run `!register <lodesetone_url> primary`.\nYour lodestone code is"
            f" `{bio_code}`")
        return

    lodestone_dict = {}
    bio = ""

    try:
        lodestone_dict = utils.get_lodestone_info(lodestone_str)
        bio = lodestone_dict["bio"]

        verification_code = "bothry-" + sha256(
            str(ctx.message.author.id).encode('utf-8')).hexdigest()
        if bio != verification_code:
            await ctx.send("Couldn't find the unique string in your lodestone "
                           "profile. Did you link the correct profile? Found: "
                           f"{bio}, expected {verification_code}")
            return

    except Exception as e:
        await ctx.send(str(e))

    fname = lodestone_dict["fname"]
    lname = lodestone_dict["lname"]
    world = lodestone_dict["world"]
    dc = lodestone_dict["dc"]
    bio = lodestone_dict["bio"]
    lodestone_id: int = lodestone_dict["lodestone_code"]

    auth_id = int(ctx.message.author.id)
    fflogs_id = fflogs.get_character_id(f"{fname} {lname}", world,
                                        utils.REGION_DICT[dc.lower()])

    if auth_id in users:
        if (fflogs_id in users[auth_id].alts or
            fflogs_id == users[auth_id].primary.fflogs_id):
            await ctx.send(
                "Tried to register a character that's already been registered."
                f" See all registered characters here:\n{users[auth_id]}")
            return

        users[auth_id].add_alt(fflogs_id, fname, lname,
                               world, dc, lodestone_id)
        await ctx.send(f"Successfully registered {fname} {lname} as an alt!")

    else:
        users[auth_id] = User.initial_user(auth_id, fflogs_id, fname, lname,
                                           world, dc, lodestone_id)
        await ctx.send(f"Successfully registered {fname} {lname} as a "
                       "primary character! Welcome!")

# @register.error
# async def register_error(ctx, e):
#     await ctx.send("The register command follows the following syntax: "
#                    f"`!register <lodestone_url>`. Got an error: {e}")

@bot.command()
async def latest(ctx, fightname=None, analysis=""):
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

@bot.command()
async def whoami(ctx):
    _, username = utils.get_id(ctx)
    await ctx.send(f"Hi {username} :hearts:")

if __name__ == "__main__":
    bot.run(bot_token)
