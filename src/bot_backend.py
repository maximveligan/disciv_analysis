import utils
from hashlib import sha256
import fflogs
from ff_user import User

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
        return f"Successfully registered {fname} {lname} as a primary character! Welcome!"
