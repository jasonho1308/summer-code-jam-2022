import random

from ..skill import Skill


class Strike(Skill):
    """Does nominal damage based on user's strength"""

    name = "Strike"
    description = "A regular hit"
    energy_cost = 0

    # Requirements for players if we get around to players learning skills
    level = 1
    strength = 1
    intelligence = 1
    stamina = 1
    dexterity = 1
    charisma = 1

    def _use(self, user, opponent):
        """Skill implementation"""
        damage = int(user.strength * (random.random() + 1))
        opponent.hp -= damage
        return f"{user.name} strikes for {damage} damage"
