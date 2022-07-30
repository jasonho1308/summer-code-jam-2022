from random import choice

class Monster:
    """Template class for monsters"""
    monster_id = None
    name = None
    level = None
    hp = None
    max_hp = None
    energy = None
    max_energy = None
    strength = None
    intelligence = None
    stamina = None
    dexterity = None
    charisma = None
    skills = []

    def attack(player):
        """Select random monster skill"""
        choice(self.skills)(self, player)
