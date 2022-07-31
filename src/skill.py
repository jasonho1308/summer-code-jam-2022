class Skill:
    """Template class for skills"""

    name: str
    description: str
    energy_cost: int

    # Requirements for players if we get around to players learning skills
    level: int
    strength: int
    intelligence: int
    stamina: int
    dexterity: int
    charisma: int

    @classmethod
    def _use(cls, user, opponent):
        """Implement effects on the user and opponent here"""
        pass

    @classmethod
    def use(cls, user, opponent):
        """Decorator for _use, used for checking if skill usable"""
        if user.energy < self.energy_cost:
            return (
                user,
                opponent,
                f"{user.name} doesn't have enough energy to cast {self.name}!",
            )
        user.energy -= self.energy_cost
        return cls._use(user, opponent)

    @classmethod
    def learnt(cls, player):
        return (
            player.level >= cls.level
            and player.strength >= cls.strength
            and player.intellegence >= cls.intelligence
            and player.stamina >= cls.stamina
            and player.dexterity >= cls.dexterity
            and player.charisma >= cls.charisma
            and player.gold >= cls.gold
        )
