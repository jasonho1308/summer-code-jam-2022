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

    def _use(self, user, opponent):
        """Implement effects on the user and opponent here"""
        pass

    def use(self, user, opponent):
        """Decorator for _use, used for checking if skill usable"""
        if user.energy < self.energy_cost:
            return (
                user,
                opponent,
                f"{user.name} doesn't have enough energy to cast {self.name}!",
            )
        user.energy -= self.energy_cost
        return self._use(user, opponent)
