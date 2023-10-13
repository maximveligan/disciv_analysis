import json
import requests as reqs
import logging

TOKEN_URL = "https://www.fflogs.com/oauth/token"
GQL_URL = "https://www.fflogs.com/api/v2/client"
TOKEN_HEADER = {'grant_type': 'client_credentials'}

with open("data.json") as f:
    data = json.load(f)
    client_id = data["client_id"]
    client_secret = data["client_secret"]
    auth_token = data["auth_token"]

headers = {
    "Content-Type": "application/json",
    "User-Agent": "WrikaBot",
    "Authorization": f"Bearer {auth_token}",
}

def fflogs_req(query):
    tmp = reqs.post(GQL_URL, json={"query": query}, headers=headers).json()
    logging.debug(tmp)
    return tmp["data"]

def get_character_id(name: str, world: str, region: str) -> int:
    query = f"""
    query {{
        characterData {{
    		character(name: "{name}", serverSlug: "{world}", serverRegion: "{region}") {{
    			canonicalID
    		}}
    	}}
    }}
    """
    character_id = fflogs_req(query)["characterData"]["character"]
    if character_id is None:
        raise Exception("Malformed character inputs.")
    else:
        return int(character_id["canonicalID"])

def get_character_name(c_id: int):
    query = f"""
    query {{
    characterData {{
    		character(id: {c_id}) {{
    			name
    		}}
    	}}
    }}
    """
    name = fflogs_req(query)["characterData"]["character"]["name"]
    if name is None:
        raise Exception(f"Invalid character id {c_id}")

    return name

def get_fighter_info(code, fight_id, username):
    query = f"""
    query {{
    reportData {{
        report(code: "{code}") {{
            table(fightIDs: [{fight_id}])
        }}
    }}
    }}
    """
    comp = fflogs_req(
        query)["reportData"]["report"]["table"]["data"]["composition"]
    for c in comp:
        if c['name'] == username:
            return c

def get_fight_id(url: str, code: str):
    fight_symbol = url.split("fight=")[1].split('&')[0]
    fight_id = 0
    if fight_symbol == "last":
        query = f"""
        query {{
        reportData {{
            report(code: "{code}") {{
                fights() {{
                    id
                }}
            }}
        }}
        }}
        """
        for fight_dict in fflogs_req(query)["data"]["reportData"]["report"]["fights"]:
            if fight_id < fight_dict["id"]:
                fight_id = fight_dict["id"]
    else:
        fight_id = fight_symbol

    if fight_id == 0:
        raise Exception("Somehow got a fight ID of 0, this happens if there "
                        "was a 0 in the URL. Check the URL.")

    return fight_id

def get_encounter_id(code: str, fight_id: int):
    query = f"""
    query {{
    reportData {{
        report(code: "{code}") {{
            fights(fightIDs: [{fight_id}]) {{
				encounterID
			}}
        }}
    }}
    }}
    """
    return fflogs_req(
        query)["reportData"]["report"]["fights"][0]["encounterID"]

def get_top_rankers(encounter_id: int, metric: str, job: str):
    query = f"""
	query {{
    worldData {{
			encounter(id: {encounter_id}) {{
				characterRankings(metric: {metric}, specName: "{job}")
			}}
		}}
	}}
	"""
    return fflogs_req(
        query)["worldData"]["encounter"]["characterRankings"]["rankings"][:10]

def get_latest_fight_report(c_id: int, encounter_id: int):
    query = f'''
    query {{
    characterData {{
        character(id: {c_id}) {{
            encounterRankings(encounterID: {encounter_id}) 
        }}
    }}
    }}
    '''
    rankings = fflogs_req(
        query)["characterData"]["character"]["encounterRankings"]["ranks"]
    start_time = 0
    tmp_rank = {}
    for rank in rankings:
        tmp = rank["startTime"]
        if tmp > start_time:
            start_time = tmp
            tmp_rank = rank

    return tmp_rank

def get_highest_fight_report(c_id: int, encounter_id: int):
    query = f'''
    query {{
    characterData {{
        character(id: {c_id}) {{
            encounterRankings(encounterID: {encounter_id}) 
        }}
    }}
    }}
    '''
    rankings = fflogs_req(
        query)["characterData"]["character"]["encounterRankings"]["ranks"]
    if not rankings:
        return {}
    else:
        return rankings[0]

def get_events(code: str, fight_id: int, source_id: int):
    query = f'''
    query {{
    reportData {{
    		report(code: "{code}") {{
    			events(fightIDs: [{fight_id}], sourceID: {source_id}) {{
    				data
    			}}
    		}}
    	}}
    }}
    '''
    return fflogs_req(query)["reportData"]["report"]["events"]["data"]
