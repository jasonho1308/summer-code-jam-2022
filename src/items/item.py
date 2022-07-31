class Item:
    """Template class for items"""

    item_type_id = None
    name = None
    slot = None
    stackable = False

    @classmethod
    def use(player):
        """Implement effects on the player on use here"""
        pass

    @classmethod
    def equipped(player):
        """Implement effects on the player while equipped here"""
        pass
