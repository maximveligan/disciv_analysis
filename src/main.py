import requests as reqs
import json
import webbrowser
import sys
import statistics
import matplotlib.pyplot as plt
import fflogs
import utils


AA_ID = 7
UNKOWN_ID = 0
ANIMATION_LOCK = 100
SLIDE_CAST_DELTA = 500
DEFAULT_CD = 2500

SHARED_ACTIONS = {}
ROLE_ACTIONS = {}

with open("actions/shared_actions.json") as f:
    SHARED_ACTIONS = json.load(f)

with open("actions/role_actions.json") as f:
    ROLE_ACTIONS = json.load(f)

def check_events(events, src_id, ffxiv_job, rel_ts=True, whitelist=["cast", "begincast"]):
    job_actions = SHARED_ACTIONS | ROLE_ACTIONS
    with open(f"actions/{utils.JOB_DICT[ffxiv_job]}_actions.json") as f:
        job_action_json = json.load(f)
        job_actions |= job_action_json["statuses"]
        job_actions |= job_action_json["actions"]

    offset = events[0]["timestamp"] if rel_ts else 0

    gcd_deltas = {}
    prev_gcd = None

    for event in events:
        if event["sourceID"] == src_id:
            ability_id = event.get("abilityGameID")

            if ability_id is None or str(ability_id) not in job_actions or ability_id in [AA_ID, UNKOWN_ID]:
                continue

            ogcd = not job_actions[str(ability_id)].get("onGcd", False)

            if event["type"] in whitelist and not ogcd:
                if prev_gcd is not None:
                    delta = float(event["timestamp"] - prev_gcd) / 1000.0
                    if delta not in gcd_deltas:
                        gcd_deltas[delta] = 1
                    else:
                        gcd_deltas[delta] += 1
                    prev_gcd = None

                if job_actions[str(ability_id)].get("cooldown", DEFAULT_CD) == DEFAULT_CD:
                    prev_gcd = event["timestamp"]

                print(f"TS: {'{:.2f}'.format(round(float(event['timestamp'] - offset) / 1000.0, 2), 2)} Ability: {job_actions[str(ability_id)]['name']} Type: {event['type']}")

    clipped = 0
    not_clipped = 0
    delta_list = []
    for k, v in gcd_deltas.items():
        if k <= 2.5:
            not_clipped += v
            delta_list += ([k] * v)
        else:
            clipped += v

    print(gcd_deltas)
    # print(delta_list)
    gcd_estimate = round(statistics.mean(delta_list), 2)
    print(f"Estimated GCD: {gcd_estimate}")
    print(f"Clipped GCDs: {clipped}, not clipped GCDs: {not_clipped}")

    plt.bar(gcd_deltas.keys(), gcd_deltas.values(), 0.001)
    plt.xlabel(f"Time between casts (estimated GCD of {gcd_estimate})")
    plt.ylabel("Number of Casts")
    plt.show()



def main():
    # auth_token = requests.post(TOKEN_URL, json=TOKEN_HEADER, auth=(client_id, client_secret)).json()["access_token"]
    # response = requests.post(GRAPHQL_URL, headers=headers)
    # code = utils.parse_code(sys.argv[1])
    # fight_id = fflogs.get_fight_id(sys.argv[1], code)

    # src_id, ffxiv_job = fflogs.get_character_source_id(sys.argv[2], code, fight_id)
    # events = fflogs.get_events(code, fight_id, src_id)
    # check_events(events, src_id, ffxiv_job)

    # top_rank = get_top_rankers(get_encounter_id(code, fight_id), "rdps", ffxiv_job)[0]

    # top_rank_src_id, _ = get_character_source_id(top_rank["name"], top_rank["report"]["code"], top_rank["report"]["fightID"])

    # webbrowser.open_new(get_xiv_analysis(code, fight_id, src_id))
    # webbrowser.open_new(get_xiv_analysis(top_rank["report"]["code"], top_rank["report"]["fightID"], top_rank_src_id))
    # report = fflogs.get_latest_fight_report(15492436, utils.JOB_DICT["p9s"])["report"]
    # webbrowser.open_new(f"https://www.fflogs.com/reports/{report['code']}#fight={report['fightID']}&type=damage-done")
    # fflogs.get_character_id("wrika kuderagon", "exodus", "na")
    print(fflogs.get_character_id("Baby Teiz", "exodus", "na"))

if __name__ == "__main__":
    main()
else:
    pass
