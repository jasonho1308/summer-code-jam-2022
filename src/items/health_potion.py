from .item import Item


class HealthPotion(Item):
    """Heals player for 50 HP"""

    item_type_id = 1
    name = "health_potion"

    def use(player):
        """Heals player for 50 HP"""
        if (player.hp + 50) > player.maxhp:
            player.hp = player.maxhp
        else:
            player.hp += 50
