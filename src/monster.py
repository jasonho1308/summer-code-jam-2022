from collections import defaultdict
from random import choice

from . import monsters
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
        return choice(self.skills)(self, player)

    def drop_loot(self) -> dict:
        """Generate loot"""
        pass


class MonsterCatalog:
    """Wrapper for organising monsters"""

    def __init__(self):
        """Organise monsters by level"""
        self.catalog = defaultdict(list)
        [
            self.catalog[cls.level].append(cls)
            for name, cls in monsters.__dict__.items()
            if isinstance(cls, type)
        ]

    def select_level(self, level):
        """Pick a random level appropriate monster"""
        return choice(self.catalog[level])
