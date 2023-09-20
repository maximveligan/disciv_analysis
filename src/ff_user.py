import ff_character

class User(object):
    def __init__(self, discord_id: int, primary, alts):
        self.discord_id = discord_id
        self.primary = primary
        self.alts = alts

    def __str__(self):
        alts_str = "Alts: " + ('\n' + '\n'.join([str(v) for v in self.alts.values()]) if self.alts else "None")
        return f"Primary: {self.primary}\n\n{alts_str}"

    @staticmethod
    def initial_user(disc_id: int, fflogs_id: int, firstname: str,
                     lastname: str, world: str, dc: str, lodestone_id: int):
        primary = ff_character.Character(
            fflogs_id, firstname, lastname, world, dc, lodestone_id)
        return User(disc_id, primary, [])

    @staticmethod
    def from_dict(id: int, user_data):
        primary = ff_character.Character.from_dict(user_data["primary"])
        alts = {fflogs_id: ff_character.Character.from_dict(alt_dict) for fflogs_id, alt_dict in user_data["alts"].items()}
        return User(id, primary, alts)

    def to_dict(self):
        return { 
            self.discord_id: {
                "primary": self.primary,
                "alts": self.alts
            }
        }

    def add_alt(self, fflogs_id, firstname, lastname, world, dc, lodestone_id):
        self.alts[fflogs_id] = ff_character.Character(
            fflogs_id, firstname, lastname, world, dc, lodestone_id)
