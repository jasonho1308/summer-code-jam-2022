class Skill:
    """Template class for skills"""

    skill_id = None
    name = None
    description = None
    effects = None
    energy_cost = None

    # Requirements for players if we get around to players learning skills
    level = None
    strength = None
    intelligence = None
    stamina = None
    dexterity = None
    charisma = None

    def _use(self, user, opponent):
        """Implement effects on the user and opponent here"""
        pass

    def use(self, user, opponent):
        """Decorator for _use, used for checking if skill usable"""
        if user.hp <= 0 and opponent.hp <= 0:
            return (user, opponent, "You both are dead, no rewards")
        if user.hp <= 0:
            return (user, opponent, f"{user.name} is dead, {opponent.name} wins")
        elif opponent.hp <= 0:
            return (user, opponent, f"{opponent.name} is dead, {user.name} wins")
        if user.energy < energy_cost:
            return (user, opponent, f"{user.name} don't have enough energy to cast {self.name}!")
        user.energy -= energy_cost
        return  _use(user, opponent)
