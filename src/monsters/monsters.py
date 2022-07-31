from .. import skills
from .monster import Monster


class Goldfish(Monster):
    """A pathetic adversary"""

    name = "Goldfish"
    level = 1
    hp = 100
    max_hp = 100
    energy = 0
    max_energy = 0
    strength = 20
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [skills.strike]


class Quokka(Monster):
    """A smiley rat"""

    name = "Quokka"
    level = 1
    hp = 250
    max_hp = 250
    energy = 0
    max_energy = 0
    strength = 20
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [skills.strike]
