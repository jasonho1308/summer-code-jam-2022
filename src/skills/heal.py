import random

from .skill import Skill


class Heal(Skill):
    """Heals caster"""

    description = "Heal yourself"
    chance = 0.85
    energy_cost = 1

    # Skill requirements for players
    level = 1
    strength = 1
    intelligence = 1
    stamina = 1
    dexterity = 1
    charisma = 1

    def _use(self, caster, _) -> str:
        """Skill implementation"""
        if random.random() > self.chance:
            return f"{caster.name!r} tried to heal, but failed miserably"

        effectiveness = random.random()
        if effectiveness < 0.3:
            if caster.max_hp - caster.hp > 0.2 * caster.intelligence:
                caster.hp = caster.max_hp
            else:
                caster.hp += int(0.1 * caster.intelligence)
            return f"{caster.name!r} healed themself for {0.1 * caster.intelligence} HP!"
        elif 0.3 < effectiveness < 0.9:
            if caster.max_hp - caster.hp > 0.5 * caster.intelligence:
                caster.hp = caster.max_hp
            else:
                caster.hp += int(0.5 * caster.intelligence)
            return f"{caster.name!r} healed themself for {0.5 * caster.intelligence} HP!"
        else:
            if caster.max_hp - caster.hp > caster.intelligence:
                caster.hp = caster.max_hp
            else:
                caster.hp += caster.intelligence
            return f"{caster.name!r} healed themself for {caster.intelligence} HP!"
