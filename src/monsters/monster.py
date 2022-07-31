import random
from collections import defaultdict

from ..skills.skill import Skill


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

    @property
    def name(self):
        """The name of the monster's type"""
        return self.__class__.__name__

    def attack(self, player):
        """Select random monster skill"""
        # TODO: Add energy cost check if monster has skill that costs energy
        return random.choice(self.skills).use(self, player)

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

    def select_monster_of_level(self, level):
        """Pick a random level appropriate monster"""
        return random.choice(self.catalog[level])()
