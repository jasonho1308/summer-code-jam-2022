import random
from collections import defaultdict

from ..skill import Skill


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
        return random.choice(self.skills)(self, player)

    def drop_loot(self) -> dict:
        """Generate loot"""
        pass


class MonsterCatalog:
    """Wrapper for organising monsters"""

    def __init__(self):
        """Organise monsters by level"""
        from . import all_monsters

        self.catalog = defaultdict(list)
        for monster in all_monsters:
            self.catalog[monster.level].append(monster)

    def select_level(self, level):
        """Pick a random level appropriate monster"""
        return random.choice(self.catalog[level])
