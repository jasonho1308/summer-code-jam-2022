from ..skill import Skill


class Bite(Skill):
    """Does nominal damage based on user's strength"""

    description = "A small little nip"
    energy_cost = 0
    chance = 0.65

    # Requirements for players if we get around to players learning skills
    level = 1
    strength = 1
    intelligence = 1
    stamina = 1
    dexterity = 1
    charisma = 1
