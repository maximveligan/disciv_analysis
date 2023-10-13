import utils
from hashlib import sha256
import fflogs
from ff_user import User
import calendar
import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import discord
from typing import Optional
import time

FFLOGS_TIMEOUT = 30
ABOUT_XPATH = "/html/body/div/div[2]/div[2]/div/div[1]/div/div/div"
SHOW_MINOR_XPATH = "/html/body/div/div[2]/div[2]/div/div[3]/div[2]/div[1]"
XIV_ANALYSIS_URL = "https://xivanalysis.com/logo.png"

def register(author_id, lodestone_url, users):
    lodestone_dict = {}
    bio = ""

    lodestone_dict = utils.get_lodestone_info(lodestone_url)
    bio = lodestone_dict["bio"]

    verification_code = "bothry-" + sha256(
        str(author_id).encode('utf-8')).hexdigest()
    if bio != verification_code:
        raise Exception("Couldn't find the unique string in your lodestone "
                       "profile. Did you link the correct profile? Found: "
                       f"{bio}, expected {verification_code}")

    fname = lodestone_dict["fname"]
    lname = lodestone_dict["lname"]
    world = lodestone_dict["world"]
    dc = lodestone_dict["dc"]
    bio = lodestone_dict["bio"]
    lodestone_id: int = lodestone_dict["lodestone_code"]

    auth_id = int(author_id)
    fflogs_id = fflogs.get_character_id(f"{fname} {lname}", world,
                                        utils.REGION_DICT[dc.lower()])

    if auth_id in users:
        if (fflogs_id in users[auth_id].alts or
            fflogs_id == users[auth_id].primary.fflogs_id):
            raise Exception(
                "Tried to register a character that's already been registered."
                f" See all registered characters here:\n{users[auth_id]}")

        users[auth_id].add_alt(fflogs_id, fname, lname,
                               world, dc, lodestone_id)
        return f"Successfully registered {fname} {lname} as an alt!"

    else:
        users[auth_id] = User.initial_user(auth_id, fflogs_id, fname, lname,
                                           world, dc, lodestone_id)
        return (f"Successfully registered {fname} {lname} as a primary "
                 "character! Welcome!")


def get_sorted_fight(fight: Optional[utils.Encounter], uid, sort_method):
    fight_info = {}
    actual_encounter = None

    retrieve_func = None
    if sort_method == "TIME":
        retrieve_func = fflogs.get_latest_fight_report
        index = "startTime"
    elif sort_method == "RANK":
        retrieve_func = fflogs.get_highest_fight_report
        index = "rankPercent"
    else:
        raise Exception(f"Unsupported sort method {sort_method}")

    if fight is None:
        for encounter in utils.Encounter:
            try:
                cur_fight = retrieve_func(uid, encounter.value)
                if not fight_info or cur_fight[index] > fight_info[index]:
                    fight_info = cur_fight
                    actual_encounter = encounter
            except KeyError:
                    continue

    else:
        fight_info = retrieve_func(uid, fight.value)
        actual_encounter = fight

    return fight_info, actual_encounter


def format_fight_message(fight, username, encounter):
    report = fight["report"]
    fight_url = utils.gen_report_url(report["code"], report["fightID"])

    start_time = datetime.datetime.fromtimestamp(fight['startTime'] / 1000.0)
    _, minutes, seconds = utils.ms_to_time(fight['duration'])

    start_time_str = (
        f"{calendar.month_abbr[start_time.month]} {start_time.day}, "
        f"{start_time.year}"
    )

    if seconds < 10:
        seconds = f"0{seconds}"
    else:
        seconds = str(seconds)

    parse = float(fight['rankPercent'])
    parse_color = utils.ParseColor.from_parse(parse)
    parse_str = "%.1f" % round(parse, 2)

    embed = discord.Embed(color=parse_color.value[0])

    summary_str = (
        f"* Parse: {parse_str}%\n"
        f"* Duration: {minutes}:{seconds}\n"
        f"* Date: {start_time_str}\n"
    )

    job = utils.Job.try_from_str(fight["spec"])

    embed.add_field(name=f"{encounter.name()}", value=summary_str, inline=True
        ).set_thumbnail(url=encounter.url()
        ).set_author(name=username, url=fight_url, icon_url=job.url()
        ).set_footer(text="Powered by FFlogs", icon_url="https://assets.rpglogs.com/img/ff/favicon.png?v=2")

    return embed, parse_color

def pull_checklist(soup: BeautifulSoup, embed: discord.Embed):
    checklist = soup.find_all(
        "div", {"class": ["title Checklist-module_title__2R2KC",
                          "active title Checklist-module_title__2R2KC"]})
    
    checklist_str = ""

    for item in checklist:
        replace_text = None
        if item.find("span"):
            replace_text = item.span.text

        spl = re.split(r'(\d+\.?\d*\%)', item.text)
        emoji = ":white_check_mark:" if item["class"] == ["title", "Checklist-module_title__2R2KC"] else ":x:"
        new_line = f"{emoji}  **{spl[0]}**: {spl[1]}\n"

        if replace_text is not None:
            try:
                new_line = f"{emoji}  **{spl[0]}**: {spl[1]}\n".replace(replace_text, utils.ABILITIES[item.span.text][0])
            except KeyError as e:
                print(f"THERE'S NO EMOJI FOR {e}")
                new_line = f"{emoji}  **{spl[0]}**: {spl[1]}\n"

        checklist_str += new_line

    embed.add_field(name="Checklist", value=checklist_str, inline=False)

def pull_suggestions(soup: BeautifulSoup, embed: discord.Embed):
    suggestions = soup.find_all(
        "div", {"class": ["Suggestions-module_extra__3kAoW"]})

    morbid = []
    major = []
    medium = []
    minor = []

    for item in suggestions:
        text = item.text
        if item.find("span"):
            alls = item.find_all("a", {"class": ["DbLink-module_link__2I_vM"]})
            for a in alls:
                try:
                    text = text.replace(a.text, utils.ABILITIES[a.text][0])
                except KeyError as e:
                    print(f"THERE'S NO EMOJI FOR {e}")

        if text.startswith("Morbid"):
            morbid.append(text[6:])
        elif text.startswith("Major"):
            major.append(text[5:])
        elif text.startswith("Medium"):
            medium.append(text[6:])
        elif text.startswith("Minor"):
            minor.append(text[5:])

    suggestions_str = ""    

    if morbid:
        suggestions_str += "\n* **Morbid**"
        for suggestion in morbid:
            suggestions_str += f"\n * {suggestion}"

    if major:
        suggestions_str += "\n* **Major**"
        for suggestion in major:
            suggestions_str += f"\n * {suggestion}"

    if medium:
        suggestions_str += "\n* **Medium**"
        for suggestion in medium:
            suggestions_str += f"\n * {suggestion}"

    if minor:
        suggestions_str += "\n* **Minor**"
        for suggestion in minor:
            suggestions_str += f"\n * {suggestion}"
    
    if not minor and not medium and not major and not morbid:
        suggestions_str += "\n* No suggestions here!"
    
    embed.add_field(name="Suggestions", value=suggestions_str, inline=False)

def pull_stats(soup: BeautifulSoup, embed: discord.Embed):
    stats_str = ""

    simple_stats = soup.find_all("div", {"class": ["SimpleStatistic-module_simpleStatistic__2uROS"]})

    for simple_stat in simple_stats:
        spl = re.split(r'(\d+\.?\d*)', simple_stat.text)
        stats_str += f"\n* __{spl[0]}:__ {''.join(spl[1:])}"

    embed.add_field(name="Statistics", value=stats_str, inline=False)


def pull_defensives(soup: BeautifulSoup, embed: discord.Embed):
    defensives = soup.find(lambda tag: tag.name == "div" and tag.text == "Defensives" and tag.get("class") == ["ui", "header"]).parent.find_all(lambda tag: tag.name == "div" and tag.get("class") == ["title"])

    defensive_str = ""

    for defensive in defensives:
        spl = defensive.text.split(" - ", 1)
        try:
            emoji = " " + utils.ABILITIES.get(spl[0], "")[0]
            ability_id = str(utils.ABILITIES.get(spl[0], "")[1])
            defensive_str += f"\n* [{spl[0]}](https://www.garlandtools.org/db/#action/{ability_id}){emoji}: {spl[1]}"
        except IndexError:
            print(f"THERE'S NO EMOJI FOR {spl[0]}, we also need the garlond code")
            defensive_str += f"\n* {spl[0]}: {spl[1]}"

    embed.add_field(name="Defensives", value=defensive_str, inline=False)


def get_analysis_page(url: str, browser):
    browser.get(url)
    wait = WebDriverWait(browser, FFLOGS_TIMEOUT)
    wait.until(
        EC.text_to_be_present_in_element((By.XPATH, ABOUT_XPATH), "About"))
    
    browser.find_element(By.XPATH, SHOW_MINOR_XPATH).click()
    return BeautifulSoup(browser.page_source, "html.parser")


def get_analysis(soup, url, color: utils.ParseColor):
    embed = discord.Embed(color=color.value[0]).set_footer(
        text="Powered by XIV Analysis", icon_url=XIV_ANALYSIS_URL).set_author(
            name="XIV Analysis", url=url, icon_url=XIV_ANALYSIS_URL)

    pull_checklist(soup, embed)
    pull_suggestions(soup, embed)
    pull_stats(soup, embed)
    pull_defensives(soup, embed)

    return embed