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

    @commands.command()
    async def fight(self, ctx, url):
        pass

    @commands.command()
    async def debug(self, ctx, analysis_url):
        if str(ctx.author) != "veli8008" and str(ctx.author) != "velitest_48463" and str(ctx.author) != "teiz":
            await ctx.send("Debugging is only permitted by the server owner!")
            return
        code, fight_id, source_id = utils.analysis_url_to_parts(analysis_url)
        soup = None

        filename = f".\\cached_analysis\\{code}_{fight_id}_{source_id}.txt"

        try:
            with open(filename, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
        except Exception:
            self.init_browser()
            soup = bot_backend.get_analysis_page(analysis_url, self.browser)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(soup))

        analysis_result = bot_backend.get_analysis(
            soup, analysis_url,
            utils.ParseColor.ORANGE)

        await ctx.send(embed=analysis_result)

    @commands.command()
    async def latest(self, ctx, *, arg: Optional[str]):
        await self.get_fight_info(ctx, arg, "TIME")

    @commands.command()
    async def highest(self, ctx, *, arg: Optional[str]):
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
        else:
            raise Exception(str(error))

    @commands.command()
    async def whoami(self, ctx):
        print(ctx.message.author.name, ctx.message.author.id)

        fflogs.get_character_id("Coldest Coffee", "Exodus", "na")

        user = self.get_character(ctx)
        if user.firstname == "Wrika":
            await ctx.send("My creator :pray:")
        else:
            await ctx.send(f"Hi {user.firstname} {user.lastname} :hearts:!")

    @whoami.error
    async def info_error(self, ctx, error):
        if isinstance(error, utils.UnregisteredUser):
            await ctx.send("User not found. Did you register using the `!register` command already?")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Bothry(bot, init_browser=False))
