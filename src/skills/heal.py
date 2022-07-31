import random

from .skill import Skill


class Heal(Skill):
    """Heals caster"""

    chance = 0.85

    def _use(self, caster, castee) -> str:
        """Skill implementation"""
        if random.random() > self.chance:
            return f"{caster.name} tried to heal, but failed miserably"

        effectiveness = random.random()
        if effectiveness < 0.3:
            if caster.maxhp - caster.hp > 0.2 * caster.intellegence:
                caster.hp = caster.maxhp
            else:
                caster.hp += int(0.1 * caster.intellegence)
            return f"{caster.name}'s heal is not so effective"
        elif 0.3 < effectiveness < 0.9:
            if caster.maxhp - caster.hp > 0.5 * caster.intellegence:
                caster.hp = caster.maxhp
            else:
                caster.hp += int(0.5 * caster.intellegence)
            return f"{caster.name}'s heal is effective"
        else:
            if caster.maxhp - caster.hp > caster.intellegence:
                caster.hp = caster.maxhp
            else:
                caster.hp += caster.intellegence
            return f"{caster.name}'s heal is super effective!"
