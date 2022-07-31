import json

from src.models import Player

from . import database


class Shop:
    """class for Shop"""

    def __init__(self) -> None:
        self.item = json.load(open("src/shop.json"))["item"]

    def buy_item(self, user_id: int, item: str):
        """Buy an item from the shop"""
        with database.SessionLocal() as db:
            money = db.query(Player.gold).filter(database.Player.UUID == user_id)
            if item in self.item.keys():
                if money < self.item[item]:
                    return "You don't have enough money!"
                db.query(Player.gold).filter(database.Player.UUID == user_id).update(
                    {"gold": money - self.item[item]}
                )
                if item == "energy_drink":
                    db.query(Player.energy).filter(
                        database.Player.UUID == user_id
                    ).update(
                        {
                            "energy": db.query(Player.energy).filter(
                                database.Player.UUID == user_id
                            )
                            + 25
                        }
                    )
                elif item == "health_potion":
                    db.query(Player.hp).filter(database.Player.UUID == user_id).update(
                        {
                            "hp": db.query(Player.hp).filter(
                                database.Player.UUID == user_id
                            )
                            + 10
                        }
                    )
                return f"You bought a {item}!"
            else:
                return "Sorry, we don't have that item."

    def display_shop(self):
        """Display the shop"""
        result = "Welcome! We've these\n====================\n"
        for item in self.item:
            result += f"{item}{' '*(15 - len(item))}- ${self.item[item]}\n"
        result += "====================\n"
        return result
