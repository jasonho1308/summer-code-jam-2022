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
            if caster.maxhp - caster.hp > 0.2 * caster.intelligence:
                caster.hp = caster.maxhp
            else:
                caster.hp += int(0.1 * caster.intelligence)
            return f"{caster.name!r} healed themself for {0.1 * caster.intelligence} HP!"
        elif 0.3 < effectiveness < 0.9:
            if caster.maxhp - caster.hp > 0.5 * caster.intelligence:
                caster.hp = caster.maxhp
            else:
                caster.hp += int(0.5 * caster.intelligence)
            return f"{caster.name!r} healed themself for {0.5 * caster.intelligence} HP!"
        else:
            if caster.maxhp - caster.hp > caster.intelligence:
                caster.hp = caster.maxhp
            else:
                caster.hp += caster.intelligence
            return f"{caster.name!r} healed themself for {caster.intelligence} HP!"
