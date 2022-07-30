import random

from ..skill import Skill


class Heal(Skill):
    """Heals caster by 0.5HP * intellegence"""

    def _use(self, caster, castee):
        """Skill implementation"""
        effectiveness = random.random()
        if effectiveness < 0.3:
            if caster.maxhp - caster.hp > 0.2 * caster.intellegence:
                caster.hp = caster.maxhp
            else:
                caster.hp += int(0.1 * caster.intellegence)
            return (
                caster,
                castee,
                f"{caster.name}'s heal is not so effective",
            )
        elif 0.3 < effectiveness < 0.9:
            if caster.maxhp - caster.hp > 0.5 * caster.intellegence:
                caster.hp = caster.maxhp
            else:
                caster.hp += int(0.5 * caster.intellegence)
            return (
                caster,
                castee,
                f"{caster.name}'s heal is effective",
            )
        else:
            if caster.maxhp - caster.hp > caster.intellegence:
                caster.hp = caster.maxhp
            else:
                caster.hp += caster.intellegence
            return (
                caster,
                castee,
                f"{caster.name}'s heal is super effective!",
            )
