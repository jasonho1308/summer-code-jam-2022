from .monsters import Monster, MonsterCatalog
from .skill import Skill


class Player:
    """Template class for players"""

    name: str
    level: int
    experience: int
    hp: int
    max_hp: int
    energy: int
    max_energy: int
    strength: int
    intelligence: int
    stamina: int
    dexterity: int
    charisma: int
    gold: int

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

    def add_exp(self, amount: int):
        """Adds exp to player, if reached maximum then level up"""
        self.experience += amount
        while self.level * 100 <= self.experience:
            self.experience -= self.level * 100
            self.level += 1
            self.max_hp += 1
            self.energy += 1
            self.max_energy += 1
            self.strength += 1
            self.intelligence += 1
            self.stamina += 1
            self.dexterity += 1
            self.charisma += 1
            self.gold += 500


class PVPFight:
    """Handles Fight actions"""

    def __init__(self, offender, defender) -> None:
        """Initalizes the fight"""
        self.offender = Player(offender)
        self.offender.is_offender = True
        self.defender = Player(defender)

    def use_skill(
        self, caster: Player, castee: Player, skill: Skill
    ) -> tuple[str, int]:
        """Called when skill used

        str: combat log to send back to user
        int: combat result
            -1 = both loses
            0  = continue
            Player = winner
        """
        cast = skill.use(caster, castee)
        combat_log = cast[2]
        if caster.is_offender:
            self.offender = cast[0]  # caster
            self.defender = cast[1]  # castee
        else:
            self.offender = cast[1]  # castee
            self.defender = cast[0]  # caster
        if self.defender.hp <= 0 and self.offender.hp <= 0:
            combat_log += "\nBoth combatants have fallen."
            return combat_log, -1
        elif self.offender.hp <= 0:
            combat_log += f"\n{self.offender.name} has fallen."
            self.offender.gold += self.gold_amount_got(self.offender)
            return combat_log, 2
        elif self.defender.hp <= 0:
            combat_log += f"\n{self.defender.name} has fallen"
            self.offender.gold += self.gold_amount_got(self.offender)
            return combat_log, 1
        else:
            return combat_log, 0

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

    def use_skill(self, skill: Skill) -> tuple[str, int | Player, dict]:
        """Run one round of combat

        str: combat log to send back to user
        int: combat result. -1 is player loss, 0 is combat continues,
            if Player is returned it's the winner
        dict: rewards for player win.
        """
        combat = skill.use(self.player, self.monster)
        self.player = combat[0]
        self.monster = combat[1]  # to update
        combat_log = combat[2]
        if self.player.hp > 0 and self.monster.hp > 0:
            monster_cast = self.monster.attack(self.player)
            self.player = combat[1]
            self.monster = combat[0]
            combat_log += "\n" + monster_cast[2]

        if self.player.hp <= 0 and self.monster.hp <= 0:
            combat_log += "\nBoth combatants have fallen."
            return combat_log, -1
        elif self.player.hp <= 0:
            combat_log += "\nYou have fallen."
            return combat_log, -1
        elif self.monster.hp <= 0:
            combat_log += (
                f"\nYou have defeated {self.monster.name}.\n+10 EXP\n+100 Gold"
            )
            self.player.add_exp(10)
            self.player.gold += 100
            return combat_log, self.player, self.monster.generate_loot()
        else:
            return combat_log, 0
