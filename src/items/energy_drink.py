from .item import Item


class EnergyDrink(Item):
    """Refill all energy"""

    item_type_id = 2
    name = "energy_drink"

    @staticmethod
    def use(player):
        """Refill all energy"""
        player.energy = player.max_energy
