from ..skills import skills
from .monster import Monster


class Goldfish(Monster):
    """A pathetic adversary"""

    level = 1
    hp = 50
    max_hp = 50
    energy = 0
    max_energy = 0
    strength = 5
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [skills["bubble"]]


class Rat(Monster):
    """Disgustic vermin"""

    level = 1
    hp = 150
    max_hp = 150
    energy = 0
    max_energy = 0
    strength = 10
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [skills["bite"]]


class Quokka(Monster):
    """A smiley rat"""

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

    skills = [skills["bite"]]


class Bandit(Monster):
    """A mischevious so-and-so"""

    name = "Bandit"
    level = 1
    hp = 1000
    max_hp = 1000
    energy = 0
    max_energy = 0
    strength = 30
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [skills["strike"]]


class Goblin(Monster):
    """A disgusting and cheeky creature"""

    name = "Bandit"
    level = 1
    hp = 1000
    max_hp = 1000
    energy = 0
    max_energy = 0
    strength = 30
    intelligence = 0
    stamina = 0
    dexterity = 0
    charisma = 0

    skills = [skills["bite"], skills["strike"]]
