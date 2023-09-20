class Character:
    def __init__(self, fflogs_id: int, firstname: str, lastname: str,
                 world: str, dc: str, lodestone_id: int):
        self.fflogs_id = fflogs_id
        self.firstname = firstname
        self.lastname = lastname
        self.world = world
        self.dc = dc
        self.lodestone_id = lodestone_id

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.world}, {self.dc}"

    def to_dict(self):
        return {
            "fflogs_id": self.fflogs_id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "world": self.world,
            "datacenter": self.dc,
            "lodestone_id": self.lodestone_id,
        }

    @staticmethod
    def from_dict(prim_dict):
        return Character(
            prim_dict["fflogs_id"], prim_dict["firstname"],
            prim_dict["lastname"], prim_dict["world"], prim_dict["dc"],
            prim_dict["lodestone_id"]
        )
