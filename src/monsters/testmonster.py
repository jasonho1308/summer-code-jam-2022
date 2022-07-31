from ..skills.strike import Strike
from .monster import Monster


class TestMonster(Monster):
    """Testing whether stuff works"""

    name = "TestMonster v0.0.1"
    level = 1
    hp = 200
    max_hp = 200
    energy = 0
    max_energy = 0
    strength = 1
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [Strike]
