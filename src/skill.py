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

    def use(user, opponent):
        """Implement effects on the user and opponent here"""
        pass
