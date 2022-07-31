from .monster import Monster, MonsterCatalog
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

    def __init__(self, database_row):
        """Populate player data from a database row"""
        self.name = database_row.name
        self.level = database_row.level
        self.hp = database_row.hp
        self.max_hp = database_row.max_hp
        self.energy = database_row.energy
        self.max_energy = database_row.max_energy
        self.strength = database_row.strength
        self.intelligence = database_row.intelligence
        self.stamina = database_row.stamina
        self.dexterity = database_row.dexterity
        self.charisma = database_row.charisma

        self.is_offender = False
        self.amount_of_skills_used = 0


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
            return 100 * self.amount_of_skills_used
        else:
            return 150 * self.amount_of_skills_used


catalog = MonsterCatalog()


class PVEFight:
    """Handle PVE fight"""

    player: Player
    monster: Monster

    def __init__(self, player) -> None:
        """Generate a new fight"""
        self.monster = catalog.select_level(player.level)
        self.player = Player(player)

    def use_skill(self, skill: Skill) -> tuple[str, int | dict]:
        """Run one round of combat

        str: combat log to send back to user
        int: combat result. -1 is player loss, 0 is combat continues, dict return value is rewards for player win.
        """
        combat_log = skill.use(self.player, self.monster)
        if self.player.hp > 0 and self.monster.hp > 0:
            combat_log += "\n" + self.monster.attack(self.player)

        if self.player.hp <= 0 and self.monster.hp <= 0:
            combat_log += "\nBoth combatants have fallen."
            return (combat_log, -1)
        elif self.player.hp <= 0:
            combat_log += "\nYou have fallen."
            return (combat_log, -1)
        elif self.monster.hp <= 0:
            combat_log += f"\nYou have defeated {self.monster.name}."
            return (combat_log, self.monster.generate_loot())
        else:
            return (combat_log, 0)
