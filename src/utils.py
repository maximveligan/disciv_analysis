import json
import requests
from html import unescape

USERS = "./users.json"
LODESTONE_ROOT_URL = "https://na.finalfantasyxiv.com/lodestone/character/"

ENCOUNTER_ID_DICT = {
    "p9s": 88,
    "p10s": 89,
    "p11s": 90,
    "p12sp1": 91,
    "p12s": 91,
    "p12sp2": 92,
}

JOB_DICT = {
    "BlackMage": "blm",
    "Dancer": "dnc",
}

REGION_DICT = {
    "primal": "NA",
    "aether": "NA",
}

def parse_code_from_url(url: str):
    url_suffix = url.split("reports/")[1]
    return url_suffix.split("#")[0]

def gen_xivanalysis_url(code: str, fight_id: int, source_id: int):
    return f"https://xivanalysis.com/fflogs/{code}/{fight_id}/{source_id}"

def gen_report_url(code: str, fight_id: int):
    return f"https://www.fflogs.com/reports/{code}#fight={fight_id}&type=damage-done"

def get_id(ctx):
    id = 0
    name = ""
    with open(USERS, "r") as f:
        user_data = json.load(f)[str(ctx.message.author.id)]["primary"]
        id = user_data["fflogs_id"]
        name = user_data["firstname"] + " " + user_data["lastname"]

    if id == 0:
        raise Exception("User isn't registered!")

    return id, name

def get_lodestone_info(lodestone_url):
    if not lodestone_url.startswith("https"):
        raise Exception("Input the full lodestone URL to your character.")

    page = requests.get(lodestone_url)

    if page.status_code != 200:
        raise Exception(
            f"{page.status_code}: Couldn't find character at {lodestone_url}")

    username = unescape(
        page.text.split("<title>")[1].split('|')[0].rstrip()).split()
    region_list = page.text.split("\"Home World\"></i>")[1].split()

    return {
        "fname": username[0],
        "lname": username[1],
        "world": region_list[0],
        "dc": region_list[1][1:].split("]")[0],
        "bio": page.text.split("\"character__selfintroduction\">")[1].split(
            "</div>")[0],
        "lodestone_code": int(
            lodestone_url.split("character/")[1].partition('/')[0]),
    }

def ms_to_time(ms_time: int):
    seconds = ms_time / 1000.0

    (hours, seconds) = divmod(seconds, 3600)
    (minutes, seconds) = divmod(seconds, 60)

    return (round(hours), round(minutes), round(seconds))
