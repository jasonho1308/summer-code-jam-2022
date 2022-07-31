class Item:
    """Template class for items"""

    item_type_id = None
    name = None
    slot = None
    stackable = False

    @staticmethod
    def use(player):
        """Implement effects on the player on use here"""
        pass

    @staticmethod
    def equipped(player):
        """Implement effects on the player while equipped here"""
        pass
