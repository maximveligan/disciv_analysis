from discord.ext import commands
import json
import utils
from hashlib import sha256
from ff_user import User
from ff_character import Character
import bot_backend
from typing import Optional
import fflogs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from sys import platform
import discord
import time

USERS_PATH = "./users.json"

class Bothry(commands.Cog):
    def __init__(self, bot, init_browser=True):
        self.bot = bot
        self.users = {}
        self.browser = None

        if init_browser:
            self.init_browser()

        with open(USERS_PATH, "r") as f:
            loaded_user_data = json.load(f)
            for disc_id, user_data in loaded_user_data.items():
                disc_id = int(disc_id)
                self.users[disc_id] = User.from_dict(disc_id, user_data)

    def init_browser(self):
        if "win" in platform:
            options = Options()
            options.binary_location = "C:\\Users\\maxim\\Downloads\\chrome-win64\\chrome.exe"
            service = Service("C:\\Users\\maxim\\dev\\executables\\chromedriver.exe")
            self.browser = webdriver.Chrome(options=options, service=service)
        else:
            self.browser = webdriver.Chrome()

    @staticmethod
    def parse_name_from_args(arg: str):
        quotes_split = arg.split('"')
        args = []
        name = ""

        if len(quotes_split) == 1:
            args = arg.split()

        elif len(quotes_split) == 3:
            before = quotes_split[0]
            after = quotes_split[2]
            name = quotes_split[1]
            rest = ""

            if before:
                rest += before.strip()

            if after:
                rest += after.strip()

            args = rest.split()

        else:
            raise commands.BadArgument(
                "Mismatched quotes in argument, check if your character name "
                "has an opening and closing quote mark (\")"
            )

        return (args, name)

    @staticmethod
    def parse_args(arg: str):
        encounter = None
        analysis = False
        job = None

        if not arg:
            return encounter, analysis, "", job

        args, name = Bothry.parse_name_from_args(arg)
        potential_errors = []

        for arg in args:
            # Try to parse as an encounter first
            try:
                encounter = utils.Encounter.try_from_str(arg)
                continue
            except commands.BadArgument as e:
                potential_errors.append(e)
            
            # Try to parse as an analysis literal
            if not analysis:
                if utils.parse_analysis_literal(arg):
                    analysis = True
                    continue
            
            # Try to parse as a job string
            try:
                job = utils.Job.try_from_str(arg)
                continue
            except commands.BadArgument as e:
                potential_errors.append(e)
            
            # If we reached here, it means we didn't hit any continues, so it
            # must be an invalid argument.
            raise commands.BadArgument(
                f"Unable to parse argument {arg}. Got the following errors "
                "when trying to parse: " + '\n'.join(potential_errors)
            )

        return encounter, analysis, name, job

    def get_character(self, ctx, name=""):
        user_id = ctx.message.author.id 
        if user_id in self.users:
            if not name:
                return self.users[user_id].primary
            else:
                characters = []
                alt: Character
                for alt in self.users[user_id].alts:
                    if name in alt.name():
                        characters.append(alt)
                characters_len = len(characters)
                match characters_len:
                    case 0: raise utils.NoSuchCharacter(
                        f"Couldn't find an alt with the name {name}.")
                    case 1: return characters[0]
                    case _: raise utils.VagueName(
                        f"Found {characters_len} alts with the name {name}: "
                        f"{', '.join(characters)}. Use a more specific name to"
                        " filter your character.")

        else:
            raise utils.UnregisteredUser

    async def get_fight_info(self, ctx, arg, sort_string):
        encounter, analysis, name, job = Bothry.parse_args(arg)

        character: Character = self.get_character(ctx, name)

        fight_info, encounter = bot_backend.get_sorted_fight(
            encounter, character.fflogs_id, sort_string)

        if not fight_info:
            raise utils.EncounterNotFound(
                f"Did not find any logs for {encounter.name}.")

        msg, color = bot_backend.format_fight_message(
            fight_info, character.name(), encounter)

        await ctx.send(embed=msg)

        if analysis:
            report = fight_info["report"]
            fighter_info = fflogs.get_fighter_info(
                report["code"], report["fightID"], character.name())
            analysis_url = utils.gen_xivanalysis_url(
                report["code"], report["fightID"], int(fighter_info["id"]))

            if self.browser is None:
                self.init_browser()

            soup = bot_backend.get_analysis_page(analysis_url, self.browser)

            analysis_result = bot_backend.get_analysis(
                soup, analysis_url, color)
            await ctx.send(embed=analysis_result)

    # @commands.command()
    # async def debug(self, ctx, analysis_url):
    #     if str(ctx.author) != "veligains" and str(ctx.author) != "velitest_48463":
    #         await ctx.send("Debugging is only permitted by the server owner!")
    #         return
    #     code, fight_id, source_id = utils.analysis_url_to_parts(analysis_url)
    #     soup = None

    #     filename = f"./cached_analysis/{code}_{fight_id}_{source_id}.html"

    #     try:
    #         with open(filename, "r", encoding="utf-8") as f:
    #             soup = BeautifulSoup(f, "html.parser")
    #     except Exception:
    #         self.init_browser()
    #         soup = bot_backend.get_analysis_page(analysis_url, self.browser)

    #         with open(filename, "w", encoding="utf-8") as f:
    #             f.write(str(soup))

    #     analysis_result = bot_backend.get_analysis(
    #         soup, analysis_url,
    #         utils.ParseColor.ORANGE)

    #     await ctx.send(embed=analysis_result)

    # @commands.command()
    # async def test(self, ctx):
    #     test_logs = {
    #         "blm_log_url": "https://endwalker.xivanalysis.com/fflogs/tzWm98Pa31khHRNY/1/10",
    #         "rdm_log_url": "https://endwalker.xivanalysis.com/fflogs/nkb6KzwhTV7XJ8dC/123/1559",
    #         "smn_log_url": "https://endwalker.xivanalysis.com/fflogs/1pW6XKy8CxZQfnb2/1/1",
    #         "dnc_log_url": "https://endwalker.xivanalysis.com/fflogs/k7VvHCP38rqDFfQm/17/201",
    #         "brd_log_url": "https://endwalker.xivanalysis.com/fflogs/mjcBPQRw3DW2rnzG/8/300",
    #         "mch_log_url": "https://endwalker.xivanalysis.com/fflogs/1pW6XKy8CxZQfnb2/1/7",
    #         "rpr_log_url": "https://endwalker.xivanalysis.com/fflogs/Rj61r9ChBfpcVvYx/2/7",
    #         "drg_log_url": "https://endwalker.xivanalysis.com/fflogs/qfRP2HyVw7xN98kC/1/2",
    #         "sam_log_url": "https://endwalker.xivanalysis.com/fflogs/HJfrvwpP6LcNxFVY/9/1",
    #         "nin_log_url": "https://endwalker.xivanalysis.com/fflogs/1pW6XKy8CxZQfnb2/1/3",
    #         "mnk_log_url": "https://endwalker.xivanalysis.com/fflogs/79xwHGQNagB1Rzc6/15/335",
    #         "war_log_url": "https://endwalker.xivanalysis.com/fflogs/T9KZGQRV2FfAgbYB/5/2",
    #         "gnb_log_url": "https://endwalker.xivanalysis.com/fflogs/aqK1tYgzQZLBn76f/2/46",
    #         "pld_log_url": "https://endwalker.xivanalysis.com/fflogs/Rj61r9ChBfpcVvYx/2/2",
    #         "drk_log_url": "https://endwalker.xivanalysis.com/fflogs/2ATn1cQdWF9hvpZz/25/3",
    #         "whm_log_url": "https://endwalker.xivanalysis.com/fflogs/Rj61r9ChBfpcVvYx/2/3",
    #         "ast_log_url": "https://endwalker.xivanalysis.com/fflogs/79xwHGQNagB1Rzc6/15/390",
    #         "sge_log_url": "https://endwalker.xivanalysis.com/fflogs/HJfrvwpP6LcNxFVY/9/4",
    #         "sch_log_url": "https://endwalker.xivanalysis.com/fflogs/nkb6KzwhTV7XJ8dC/123/445",
    #     }

    #     for job, url in test_logs.items():
    #         await self.debug(ctx, url)

    @commands.command(
        brief="Register yourself as a new user",
        description="Run the command with no URL first to get your "
                    "registration code. Once you've put the code in your"
                    " lodestone bio, rerun the register command with your "
                    "lodestone URL.")
    async def register(self, ctx, lodestone_url: str=commands.parameter(
            default="", description="Your character's lodestone URL")):
        if not lodestone_url:
            bio_code = "bothry-" + str(
                sha256(str(ctx.message.author.id).encode('utf-8')).hexdigest())

            if ctx.message.author.id in self.users:
                await ctx.send(
                    f"Already registered {self.users[ctx.message.author.id]}.\n"
                    "To register another character, rerun this command "
                    "with `!register <character loadstone URL>` after adding\n"
                    f"`{bio_code}` to the character's loadstone bio.")
                return

            await ctx.send(
                "Input your character's lodestone URL to register. The first "
                "character you register will be your primary character. Everything"
                " else will be registered as an alt. To swap primary characters, "
                "run `!register <lodesetone_url> primary`.\nYour lodestone code is"
                f" `{bio_code}`. Rerun `!register` followed by your lodestone "
                "URL once you've updated your bio to finish registration.")
            return

        else:
            await ctx.send(bot_backend.register(ctx.message.author.id,
                           lodestone_url, self.users))

    @register.error
    async def register_error(self, ctx, e):
        if isinstance(e, utils.InvalidLodestoneURL):
            await ctx.send(
                f"Got an invalid lodestone URL: `{e}`. Make sure you paste the "
                "entire url - `!register https://<your_character_lodestone_url>`")

        elif isinstance(e, utils.BadLodestonePageCode):
            await ctx.send(f"God a bad response from lodestone: {e}. Is the "
                           "website down?")
            
        elif isinstance(e, utils.WrongVerificationCode):
            expected = "bothry-" + str(
                sha256(str(ctx.message.author.id).encode('utf-8')).hexdigest())
            await ctx.send(
                "Did not find the correct code in your profile! It should've been:\n"
                f"`{expected}`, but found\n`{e}`. Did you link the right profile?")
        
        elif isinstance(e, utils.MissingCode):
            await ctx.send(
                "No code starting with `bothry-` was found in the linked profile bio!"
                f" The following was found in the bio:\n`{e}`")

        elif isinstance(e, utils.MultipleCodes):
            await ctx.send(
                f"Found multiple codes in the bio! The following was found:\n`{e}`")
        
        else:
            raise e


    @commands.command(
        brief="Get your latest parse",
        description="Gets the latest parse uploaded to fflogs. Right now it only"
                    " looks at savage fights.")
    async def latest(self, ctx, *,
            arg: Optional[str]=commands.parameter(
                default=None,
                description="Set `a` to get analysis as well. You can also set a"
                            " fight name to filter by specific fights. The order "
                            "in which you specify the analysis/fight name does not"
                            " matter. Example: `!latest a p12sp1`")):
        await self.get_fight_info(ctx, arg, "TIME")

    @commands.command(
        brief="Get your highest parse",
        description="Gets your highest parse uploaded to fflogs. Right now only "
                    "savage fights are filtered."
    )
    async def highest(self, ctx, *,
            arg: Optional[str]=commands.parameter(
                default=None,
                description="Set `a` to get analysis as well. You can also set a"
                            " fight name to filter by specific fights. The order "
                            "in which you specify the analysis/fight name does not"
                            " matter. Example: `!highest a p12sp1`")):
        await self.get_fight_info(ctx, arg, "RANK")

    @highest.error
    @latest.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            encounters_str = ""

            for encounter in utils.Encounter:
                encounters_str += f"{encounter.name}, "

            await ctx.send(
                f"{error}. Supported encounters are: {encounters_str[:-2]}")

        elif isinstance(error, commands.BadLiteralArgument):
            await ctx.send(
                "To include an analysis URL, specify either \"a\" or "
                "\"analysis\". Example: `!highest p11s a` or "
                "`!highest p11s analysis`"
            )
        elif isinstance(error, utils.EncounterNotFound):
            await ctx.send(error)
        elif isinstance(error, utils.UnregisteredUser):
            await ctx.send(
                "You haven't registered your character yet! Please run `!register`")
        else:
            raise Exception(str(error))

    @commands.command(
        brief="Prints the registered character associated with your discord ID",
        description="Prints the registered character associated with your discord ID"
    )
    async def whoami(self, ctx):
        user = self.get_character(ctx)
        await ctx.send(f"Hi {user.firstname} {user.lastname} :hearts:!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @whoami.error
    async def info_error(self, ctx, error):
        if isinstance(error, utils.UnregisteredUser):
            await ctx.send("User not found. Did you register using the `!register` command already?")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Bothry(bot, init_browser=False))
