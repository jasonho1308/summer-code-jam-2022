import random


class Skill:
    """Template class for skills"""

    name: str
    description: str
    energy_cost: int
    chance: float

    # Requirements for players if we get around to players learning skills
    level: int
    strength: int
    intelligence: int
    stamina: int
    dexterity: int
    charisma: int

    @property
    def name(self):
        """The name of the skill"""
        return self.__class__.__name__

    def _use(self, user, opponent):
        """Skill implementation"""
        if random.random() < self.chance:
            damage = int(user.strength * (random.random() + 1))
            opponent.hp -= damage
            return f"{user.name!r} uses {self.name!r} for {damage} damage"
        else:
            return f"{user.name!r} tried to use {self.name!r} but missed!"

    def use(self, user, opponent):
        """Decorator for _use, used for checking if skill usable"""
        if user.energy < self.energy_cost:
            return (
                user,
                opponent,
                f"{user.name!r} doesn't have enough energy to cast {self.name!r}!",
            )
        user.energy -= self.energy_cost
        return self._use(user, opponent)

    @classmethod
    def learnt(cls, player):
        """Check if skill is learnt by user"""
        return (
            player.level >= cls.level
            and player.strength >= cls.strength
            and player.intellegence >= cls.intelligence
            and player.stamina >= cls.stamina
            and player.dexterity >= cls.dexterity
            and player.charisma >= cls.charisma
            and player.gold >= cls.gold
        )
