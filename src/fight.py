from .skill import Skill


class Player:
    """Template class for players"""

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

    is_offender: bool
    amount_of_skills_used: int


class Fight:
    """Handles Fight actions"""

    def __init__(self, offender: Player, defender: Player) -> None:
        """Initalizes the fight"""
        self.offender = offender
        self.defender = defender

    def use_skill(self, caster: Player, castee: Player, skill: Skill) -> str:
        """Called when one uses skill"""
        cast = skill.use(caster, castee)
        if caster.is_offender:
            self.offender = cast[0]  # caster
            self.defender = cast[1]  # castee
        else:
            self.offender = cast[1]  # castee
            self.defender = cast[0]  # caster
        return cast[3]  # whether the skill was effective or not

    def gold_amount_got(self, winner: Player) -> int:
        """Calculate the gold obtained when one wins"""
        if winner.is_offender:
            return 100 * amount_of_skills_used
        else:
            return 150 * amount_of_skills_used

            
    
