from .item import Item


class HealthPotion(Item):
    """Heals player for 50 HP"""

    item_type_id = 1
    name = "health_potion"

    @staticmethod
    def use(player):
        """Heals player for 50 HP"""
        if (player.hp + 50) > player.max_hp:
            player.hp = player.max_hp
        else:
            player.hp += 50
