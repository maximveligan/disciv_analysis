import requests
from html import unescape
from enum import Enum
from discord.ext import commands
import discord

USERS = "./users.json"
LODESTONE_ROOT_URL = "https://na.finalfantasyxiv.com/lodestone/character/"
ANALYSIS_STRS = ["analyze", "analysis", 'a']

ABILITIES = {
    "Shield Samba": ("<:Shield_Samba:1159408355677319169>", 16012),
    "Second Wind": ("<:Second_Wind:1159408354167373854>", 7541),
    "Improvisation": ("<:Improvisation:1159408353211072633>", 16014),
    "Curing Waltz": ("<:Curing_Waltz:1159408351306842202>", 16015),
    "Addle": ("<:Addle:1159574579581300856>", 7560),
    "Manaward": ("<:Manaward:1159574581707821077>", 157),
    "Sharpcast": ("<:sharpcast:1159670308651929712>", 0),
    "Fire": ("<:f1:1159670306202472550>", 0),
    "Paradox": ("<:para:1159407394359611412>", 0),
    "Blizzard IV": ("<:b4:1159670311214661632>", 0),
    "Despair": ("<:despair:1159407395433353286>", 0),
    "Thunder III": ("<:t3:1159670310044450877>", 0),
    "Ley Lines": ("<:ll:1159670307993419816>", 0),
    "Auto Attack": ("<:aa:1159724694350594149>", 0),
    "Standard Finish": ("<:standard_finish:1159729155416539197>", 0),
    "Dance Partner": ("<:dance_partner:1159729359825936424>", 0),
    "Technical Finish": ("<:tech_finish:1159729569620836362>", 0),
    "Fan Dance": ("<:fan_dance:1159729787930157186>", 0),
    "Holmgang": ("<:holmgang:1159731710859153468>", 43),
    "Vengeance": ("<:vengence:1159731705641435157>", 44),
    "Bloodwhetting": ("<:bloodwhetting:1159731707126222848>", 25751),
    "Shake It Off": ("<:shake_it_off:1159731702189543434>", 7388),
    "Nascent Flash": ("<:nascent:1159731712067108906>", 16464),
    "Thrill of Battle": ("<:nascent:1159731712067108906>", 40),
    "Equilibrium": ("<:equilibrium:1159731708598423635>", 3552),
    "Rampart": ("<:rampart:1159731699077365770>", 7531),
    "Reprisal": ("<:reprisal:1159731700327268412>", 7535),
    "No Mercy": ("<:no_mercy:1159735801328979998>", 0),
    "Camouflage": ("<:camouflage:1159737428299501588>", 16140),
    "Aurora": ("<:aurora:1159737426445615174>", 16151),
    "Heart of Corundum": ("<:heart_of_corundum:1159737430585393283>", 25758),
    "Heart of Light": ("<:heart_of_light:1159737432099528714>", 16160),
    "Nebula": ("<:nebula:1159737434305744946>", 16148),
    "Superbolide": ("<:superbolide:1159737435857625138>", 16152),
    "Manafont": ("<:manafont:1159924874387652648>", 0),
    "Liturgy of the Bell": ("<:lob:1159756507081093120>", 25862),
    "Asylum": ("<:asylum:1159756505789247528>", 3569),
    "Aquaveil": ("<:aquaveil:1159756503859871758>", 25861),
    "Divine Benison": ("<:benis:1159756508372938803>", 7432),
    "Temperance": ("<:temperance:1159756793564626985>", 16536),
    "Pneuma": ("<:pneuma:1159756521870209034>", 24318),
    "Holos": ("<:holos:1159756737558093884>", 24310),
    "Panhaima": ("<:panhaima:1159756742826131476>", 24311),
    "Haima": ("<:haima:1159756735335125014>", 24305),
    "Physis II": ("<:physis_ii:1159756744151552021>", 24302),
    "Soteria": ("<:soteria:1159756806160134204>", 24294),
    "Rhizomata": ("<:rhizomata:1159756529235394570>", 24309),
    "Krasis": ("<:krasis:1159756739709771859>", 24317),
    "Whispering Dawn": ("<:dawn:1159756511078264862>", 16537),
    "Fey Illumination": ("<:fey:1159756514970574889>", 16538),
    "Recitation": ("<:recitation:1159756527213756506>", 16542),
    "Summon Seraph": ("<:seraph:1159756748035461150>", 16545),
    "Protraction": ("<:protraction:1159756746840080436>", 25867),
    "Expedient": ("<:expedient:1159756513246720070>", 25868),
    "Exaltation": ("<:exaltation:1159756511917133846>", 25873),
    "Celestial Intersection": ("<:intersection:1159756738665394206>", 16556),
    "Celestial Opposition": ("<:opposition:1159756741190373461>",16553),
    "Collective Unconscious": ("<:bubble:1159756509266321540>", 3613),
    "Earthly Star": ("<:earthlystar:1159756749679640596>", 7439),
    "Macrocosmos": ("<:macro:1159756518212763648>", 25874),
    "Arcane Crest": ("<:arcane_crest:1264079963213008897>", 24404),
    "Magick Barrier": ("<:magic_barrier:1264077987922444339>", 25857),
    "Triplecast": ("<:triple_cast:1264077195488526447>", 0),
    "Umbral Soul": ("<:umbral_soul:1174972466918068325>", 0),
    "Radiant Aegis": ("<:radiant_aegis:1264078290893930507>", 25799),
    "Raging Strikes": ("<:raging_strikes:1174973684042190858>", 0),
    "Nature's Minne": ("<:natures_minne:1264079974261063805>", 7408),
    "Troubadour": ("<:troubadour:1264079982515458068>", 7405),
    "Dismantle": ("<:dismantle:1264079967617024000>", 2887),
    "Tactician": ("<:tactician:1264082652625899592>", 16889),
    "Soulsow": ("<:soulsow:1264079978132275250>", 0),
    "Death's Design": ("<:deaths_design:1264079966518120499>", 0),
    "Enshroud": ("<:enshroud:1174975337503932526>", 0),
    "Arcane Circle": ("<:arcane_circle:1264083885537493114>", 0),
    "Feint": ("<:feint:1264079969890603078>", 7549),
    "Bloodbath": ("<:blood_bath:1174975724650766386>", 7542),
    "Battle Litany": ("<:battle_litany:1174976515658756206>", 0),
    "Nastrond": ("<:nastrond:1174976511883886592>", 0),
    "Lance Charge": ("<:lance_charge:1174976513523855380>", 0),
    "Stardiver": ("<:stardiver:1174976514517905478>", 0),
    "Dragon Sight": ("<:dragon_sight:1174976510919184384>", 0),
    "Higanbana": ("<:higinbana:1174978004074631198>", 0),
    "Third Eye": ("<:third_eye:1174978001763586068>", 7498),
    "Trick Attack": ("<:trick_attack:1174978469696913491>", 0),
    "Shade Shift": ("<:shade_shift:1174978471345266778>", 2241),
    "Disciplined Fist": ("<:disciplined_fist:1174979026318790677>", 0),
    "Leaden Fist": ("<:leaden_fist:1174979028273336390>", 0),
    "Leaden Fist": ("<:leaden_fist:1174979028273336390>", 0),
    "Brotherhood": ("<:brotherhood:1174979029401608233>", 0),
    "Riddle of Fire": ("<:riddle_of_fire:1174979030651506799>", 0),
    "Celestial Revolution": ("<:celestial_revolution:1174979031708475392>", 0),
    "Masterful Blitz": ("<:masterful_blitz:1174979033239392268>", 0),
    "Riddle of Earth": ("<:riddle_of_earth:1174979673587974214>", 7394),
    "Requiescat": ("<:requiescat:1174980946257248307>", 0),
    "Fight Or Flight": ("<:fight_or_flight:1174980947934990376>", 0),
    "Hallowed Ground": ("<:hallowed_ground:1159974980231102474>", 30),
    "Sentinel": ("<:sentinel:1159974981166432320>", 17),
    "Passage Of Arms": ("<:passage_of_arms:1174980951294615643>", 7385),
    "Divine Veil": ("<:divine_veil:1174980952842309702>", 3540),
    "Bulwark": ("<:bulwark:1159974978394001418>", 22),
    "Blood Weapon": ("<:blood_weapon:1174982813347479552>", 0),
    "Living Dead": ("<:living_dead:1159975448202203237>", 3638),
    "Shadow Wall": ("<:shadow_wall:1159975452358754374>", 3636),
    "Dark Missionary": ("<:dark_missionary:1174982817646657567>", 16471),
    "Oblation": ("<:oblation:1159975450588745769>", 25754),
    "Dark Mind": ("<:dark_mind:1159975444582514728>", 3634),
    "Eukrasian Dosis III": ("<:eukrasian_dosis_iii:1174984845622001714>", 0),
    "Minor Arcana": ("<:arcana:1174984849174564864>", 0),
    "Draw": ("<:draw:1174984850755833876>", 0),
    "Lightspeed": ("<:ls:1174984852144132158>", 0),
    "Divination": ("<:div:1174984853545025576>", 0),
    "Horoscope": ("<:hs:1174984854530707487>", 0),
    "Neutral Sect": ("<:neutral:1174984855927394325>", 0),
    "Infusion of Strength": ("<:strength_pot:1175010715225051136>", 0),
    "Manafication": ("not implemented yet", 0)
}

class EncounterNotFound(commands.CommandError):
    pass

class UnsupportedSort(Exception):
    pass

class UnregisteredUser(commands.CommandError):
    pass

class NoSuchCharacter(commands.CommandError):
    pass

class VagueName(commands.CommandError):
    pass

class InvalidParseNum(commands.CommandError):
    pass

class InvalidLodestoneURL(commands.CommandError):
    pass

class BadLodestonePageCode(commands.CommandError):
    pass

class WrongVerificationCode(commands.CommandError):
    pass

class MissingCode(commands.CommandError):
    pass

class MultipleCodes(commands.CommandError):
    pass

class Encounter(Enum):
    p9s = 88
    p10s = 89
    p11s = 90
    p12sp1 = 91
    p12sp2 = 92

    def name(self):
        match self:
            case Encounter.p9s: return "Kokytos"
            case Encounter.p10s: return "Pandaemonium"
            case Encounter.p11s: return "Themis"
            case Encounter.p12sp1: return "Athena"
            case Encounter.p12sp2: return "Pallas Athena"
            case _: raise Exception(f"Not sure how I got this {self}")

    @staticmethod
    def try_from_str(arg: str):
        match arg.lower():
            case "p9s": return Encounter.p9s
            case "p10s": return Encounter.p10s
            case "p11s": return Encounter.p11s
            case "p12s": raise commands.BadArgument("Please specify p12sp1 or p12sp2")
            case "p12sp1": return Encounter.p12sp1
            case "p12sp2": return Encounter.p12sp2
            case _: raise commands.BadArgument(f"Unsupported encounter: {arg}")

    def emoji(self):
        match self:
            case Encounter.p9s: return "<:kokytos:1159536393459085373>"
            case Encounter.p10s: return "<:pandaemonium:1159536396298620979>"
            case Encounter.p11s: return "<:themis:1159536398471278682>"
            case Encounter.p12sp1: return "<:athena:1159536390875385927>"
            case Encounter.p12sp2: return "<:pallas_athena:1159536394939670528>"
            case _: raise Exception(f"Not sure how I got this {self}")

    def url(self):
        return f"https://assets.rpglogs.com/img/ff/bosses/{self.value}-icon.jpg?v=2"

class ParseColor(Enum):
    GREY = 0x979C9F,
    GREEN = 0x2ECC71,
    BLUE = 0x3498DB,
    PURPLE = 0x9B59B6,
    ORANGE = 0xE67E22,
    PINK = 0xEB459F,
    GOLD = 0xF1C40F

    @staticmethod
    def from_parse(parse: float):
        if parse < 25.0:
            return ParseColor.GREY
        elif parse >= 25.0 and parse < 50.0:
            return ParseColor.GREEN
        elif parse >= 50.0 and parse < 75.0:
            return ParseColor.BLUE
        elif parse >= 75.0 and parse < 95.0:
            return ParseColor.PURPLE
        elif parse >= 95.0 and parse < 99.0:
            return ParseColor.ORANGE
        elif parse >= 99.0 and parse < 100.0:
            return ParseColor.PINK
        elif parse == 100.0:
            return ParseColor.GOLD
        else:
            raise InvalidParseNum(f"Got an invalid parse percentage {parse}.")

    def colorize(self, txt: str):
        match self:
            case ParseColor.GREY:
                return f"[2;33m[2;32m[2;30m{txt}[0m[2;32m[0m[2;33m[2;30m[0m[2;33m[0m"
            case ParseColor.GREEN:
                return f"[2;33m[2;32m{txt}[0m[2;33m[2;30m[0m[2;33m[0m"
            case ParseColor.BLUE:
                return f"[2;33m[2;32m[2;30m[2;34m{txt}[0m[2;30m[0m[2;32m[0m[2;33m[2;30m[0m[2;33m[0m"
            case ParseColor.PURPLE:
                return f"[2;35m[0m[2;31m[0m[2;35m{txt}[0m[2;33m[2;32m[2;30m[2;34m[2;35m[2;45m[0m[2;35m[0m[2;34m[0m[2;30m[0m[2;32m[0m[2;33m[2;30m[0m[2;33m[0m"
            case ParseColor.ORANGE:
                return f"[2;33m{txt}[2;30m[0m[2;33m[0m"
            case ParseColor.PINK:
                return f"[2;31m{txt}[0m[2;33m[2;32m[2;30m[2;34m[2;35m[0m[2;34m[0m[2;30m[0m[2;32m[0m[2;33m[2;30m[0m[2;33m[0m"
            case ParseColor.GOLD:
                return f"[2;31m[0m[2;33m100[0m[2;33m[2;32m[2;30m[2;34m[2;35m[0m[2;34m[0m[2;30m[0m[2;32m[0m[2;33m[2;30m[0m[2;33m[0m"

class Job(Enum):
    BlackMage = "blm",
    RedMage = "rdm",
    Summoner = "smn",
    Dancer = "dnc",
    Bard = "brd",
    Machinist = "mch",
    Reaper = "rpr",
    Dragoon = "drg",
    Samurai = "sam",
    Ninja = "nin",
    Monk = "mnk"
    Warrior = "war",
    Gunbreaker = "gnb",
    Paladin = "pld",
    DarkKnight = "drk",
    WhiteMage = "whm",
    Astrologion = "ast",
    Sage = "sge",
    Scholar = "sch",

    @staticmethod
    def try_from_str(arg: str):
        match arg:
            case "BlackMage": return Job.BlackMage
            case "RedMage": return Job.RedMage
            case "Summoner": return Job.Summoner

            case "Dancer": return Job.Dancer
            case "Bard": return Job.Bard
            case "Machinist": return Job.Machinist

            case "Reaper": return Job.Reaper
            case "Dragoon": return Job.Dragoon
            case "Ninja": return Job.Ninja
            case "Samurai": return Job.Samurai
            case "Monk": return Job.Monk

            case "Warrior": return Job.Warrior
            case "Gunbreaker": return Job.Gunbreaker
            case "Paladin": return Job.Paladin
            case "DarkKnight": return Job.DarkKnight

            case "WhiteMage": return Job.WhiteMage
            case "Astrologion": return Job.Astrologion
            case "Sage": return Job.Sage
            case "Scholar": return Job.Scholar
            case _: commands.BadArgument(f"Unsupported jobname {arg}")

    def url(self):
        match self:
            case Job.BlackMage: return "https://img.finalfantasyxiv.com/lds/promo/h/A/7JuT00VSwaFqTfcTYUCUnGPFQE.png"
            case Job.RedMage: return "https://img.finalfantasyxiv.com/lds/promo/h/C/NRnqJxzRtbDKR1ZHzxazWBBR2Y.png"
            case Job.Summoner: return "https://img.finalfantasyxiv.com/lds/promo/h/b/ZwJFxv3XnfqB5N6tKbgXKnj6BU.png"

            case Job.Dancer: return "https://img.finalfantasyxiv.com/lds/promo/h/0/ZzzbixB1HHW9FaxNXdfY7Y7lvw.png"
            case Job.Bard: return "https://img.finalfantasyxiv.com/lds/promo/h/b/d7BM1x8OZRZU-9fTk-D7g1t2oc.png"
            case Job.Machinist: return "https://img.finalfantasyxiv.com/lds/promo/h/2/oHLJxTt_OLDK_eQkRTBVNwwxeE.png"

            case Job.Reaper: return "https://img.finalfantasyxiv.com/lds/promo/h/p/y8GHAXX4qhY7D-yqnCqtEPkjoo.png"
            case Job.Dragoon: return "https://img.finalfantasyxiv.com/lds/promo/h/1/zWRkXGJIJhN7WHGGv1gVscRxmA.png"
            case Job.Ninja: return "https://img.finalfantasyxiv.com/lds/promo/h/N/EXvdQYvr1Rn4En8AKssbVwwcac.png"
            case Job.Samurai: return "https://img.finalfantasyxiv.com/lds/promo/h/J/Ra2GV79gVQhy6SwCrU19boTghc.png"
            case Job.Monk: return "https://img.finalfantasyxiv.com/lds/promo/h/C/Ce_VQB6VPPJKTGJwxf3h5iujp4.png"

            case Job.Warrior: return "https://img.finalfantasyxiv.com/lds/promo/h/0/U3f8Q98TbAeGvg_vXiHGOaa2d4.png"
            case Job.Gunbreaker: return "https://img.finalfantasyxiv.com/lds/promo/h/8/fc5PYpEFGrg4qPYDq_YBbCy1X0.png"
            case Job.Paladin: return "https://img.finalfantasyxiv.com/lds/promo/h/V/NUXU4h6iXzF8HS4BxHKYf7vOa0.png"
            case Job.DarkKnight: return "https://img.finalfantasyxiv.com/lds/promo/h/9/5JT3hJnBNPZSLAijAF9u7zrueQ.png"

            case Job.WhiteMage: return "https://img.finalfantasyxiv.com/lds/promo/h/G/Na619RGtVtbEvNn1vyFoSlvZ84.png"
            case Job.Astrologion: return "https://img.finalfantasyxiv.com/lds/promo/h/E/g7JY4S1D-9S26VarEuIkPGIrFM.png"
            case Job.Sage: return "https://img.finalfantasyxiv.com/lds/promo/h/e/G0lQTD01LdCGk5pECSc7fbbmbM.png"
            case Job.Scholar: return "https://img.finalfantasyxiv.com/lds/promo/h/s/2r8fm3U0Io7Pw1XT1tvnjPthp4.png"


REGION_DICT = {
    "primal": "NA",
    "aether": "NA",
}

def parse_analysis_literal(arg: str):
    return arg in ANALYSIS_STRS

def parse_code_from_url(url: str):
    url_suffix = url.split("reports/")[1]
    return url_suffix.split("#")[0]

def gen_xivanalysis_url(code: str, fight_id: int, source_id: int):
    # return f"http://localhost:3000/fflogs/{code}/{fight_id}/{source_id}"
    return f"https://endwalker.xivanalysis.com/fflogs/{code}/{fight_id}/{source_id}"

def gen_report_url(code: str, fight_id: int):
    return f"https://www.fflogs.com/reports/{code}#fight={fight_id}&type=damage-done"

def get_lodestone_info(lodestone_url):
    if not lodestone_url.startswith("https"):
        raise InvalidLodestoneURL(lodestone_url)

    try:
        page = requests.get(lodestone_url)
    except requests.exceptions.ConnectionError as e:
        raise InvalidLodestoneURL(lodestone_url) from e
    
    if page.status_code != 200:
        raise BadLodestonePageCode(page.status_code)

    username = unescape(
        page.text.split("<title>")[1].split('|')[0].rstrip()).split()
    region_list = page.text.split("\"Home World\"></i>")[1].split()
    
    bio = page.text.split("\"character__selfintroduction\">")[1].split("</div>")[0].split("<br />")
    
    bothry_lines = list(filter(
        lambda line: line.startswith("bothry-"),
        bio))

    if not bothry_lines:
        raise MissingCode("\n".join(bio))
    
    if len(bothry_lines) > 1:
        raise MultipleCodes("\n".join(bothry_lines))

    return {
        "fname": username[0],
        "lname": username[1],
        "world": region_list[0],
        "dc": region_list[1][1:].split("]")[0],
        "bio": bothry_lines[0],
        "lodestone_code": int(
            lodestone_url.split("character/")[1].partition('/')[0]),
    }

def ms_to_time(ms_time: int):
    seconds = ms_time / 1000.0

    (hours, seconds) = divmod(seconds, 3600)
    (minutes, seconds) = divmod(seconds, 60)

    return (round(hours), round(minutes), round(seconds))

def analysis_url_to_parts(url: str):
    spl = url.split('/')
    # Code, fight id, and then source id
    return (spl[4], spl[5], spl[6])
