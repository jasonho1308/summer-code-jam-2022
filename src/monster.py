from random import choice

from .skill import Skill


class Monster:
    """Template class for monsters"""

    name: str
    level: int
    hp: int
    max_hp: int
    energy: int
    max_energy: int
    strength: int
    intelligence: int
    stamina: int
    dexterity: int
    charisma: int
    skills: list[Skill]

    def attack(self, player):
        """Select random monster skill"""
        choice(self.skills)(self, player)
