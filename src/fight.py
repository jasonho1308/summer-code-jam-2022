from .monsters import Monster, MonsterCatalog
from .skills.skill import Skill


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

    def __init__(self, database_row) -> None:
        """Populate player data from a database row"""
        self.name = database_row.name
        self.level = database_row.level
        self.experience = database_row.experience
        self.hp = database_row.hp
        self.max_hp = database_row.max_hp
        self.energy = database_row.energy
        self.max_energy = database_row.max_energy
        self.strength = database_row.strength
        self.intelligence = database_row.intelligence
        self.stamina = database_row.stamina
        self.dexterity = database_row.dexterity
        self.charisma = database_row.charisma
        self.gold = database_row.gold

        self.is_offender = False
        self.amount_of_skills_used = 0

    def add_exp(self, amount: int) -> bool:
        """Adds exp to player, if reached maximum then level up"""
        self.experience += amount
        levelled = False
        while self.level * 100 <= self.experience:
            self.experience -= self.level * 100
            self.level += 1
            self.max_hp += 5
            self.hp = self.max_hp
            self.max_energy += 2
            self.energy = self.max_energy
            self.strength += 1
            self.intelligence += 1
            self.stamina += 1
            self.dexterity += 1
            self.charisma += 1
            levelled = True
        return levelled


class PVPFight:
    """Handles Fight actions"""

    fight_type = "PVP"

    def __init__(self, offender, defender) -> None:
        """Initalizes the fight"""
        self.offender = Player(offender)
        self.offender.is_offender = True
        self.defender = Player(defender)

    def use_skill(self, caster: Player, castee: Player, skill: Skill) -> tuple[str, int]:
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
    fight_type = "PVE"

    def __init__(self, player) -> None:
        """Generate a new fight"""
        self.monster = catalog.select_monster_of_level(player.level)
        self.player = Player(player)

    def use_skill(self, skill: Skill) -> tuple[str, int | dict]:
        """Run one round of combat

        str: combat log to send back to user
        int: combat result. -1 is player loss, 0 is combat continues,
            if dict is returned, player has won
        dict: rewards for player win.
        """
        combat_log = skill.use(self.player, self.monster)
        if self.player.hp > 0 and self.monster.hp > 0:
            combat_log += "\n" + self.monster.attack(self.player)

        if self.player.hp <= 0:
            if self.monster.hp <= 0:
                combat_log += "\nBoth combatants have fallen."
            else:
                combat_log += "\nYou have fallen."
            self.player.hp = self.player.max_hp
            self.player.energy = self.player.max_energy
            combat_log += f"\nYou find yourself back in town, your purse {int(self.player.gold * 0.75)} gold lighter"
            self.player.gold = int(self.player.gold * 0.25)
            return combat_log, -1
        elif self.player.hp <= 0:
            return combat_log, -1
        elif self.monster.hp <= 0:
            loot = self.monster.drop_loot()
            combat_log += f"\nYou have defeated {self.monster.name}.\n+{loot['xp']} EXP"
            if "gold" in loot:
                combat_log += f"\n+{loot['gold']} Gold"
                self.player.gold += loot["gold"]
            if "items" in loot:
                for i in loot["items"]:
                    combat_log += f"\nGained {i.name}"
            levelled = self.player.add_exp(loot["xp"])
            if levelled:
                combat_log += f"\nLevelled up! You are now level {self.player.level}."
            return combat_log, loot
        else:
            return combat_log, 0
