class Item:
    """Template class for items"""

    item_type_id = None
    name = None
    slot = None
    stackable = False

    def use(player):
        """Implement effects on the player on use here"""
        pass

    def equipped(player):
        """Implement effects on the player while equipped here"""
        pass
