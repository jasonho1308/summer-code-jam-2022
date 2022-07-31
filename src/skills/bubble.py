from .skill import Skill


class Bubble(Skill):
    """Does nominal damage based on user's strength"""

    description = "Did they just spit at you?!"
    energy_cost = 0
    chance = 0.5

    # Skill requirements for players
    level = 1
    strength = 1
    intelligence = 1
    stamina = 1
    dexterity = 1
    charisma = 1
