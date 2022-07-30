import bcrypt
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from . import database, models


class ActionManager:
    """Handling actions from client"""

    certificated = {}

    async def login(self, data, client_id, connection_manager, websocket):
        """
        Handles login request

        JSON Structure:
        {
            "action": "login"
            "name": "xxx"
            "password": "xxx"
        }
        """
        db = database.SessionLocal()
        hashed = db.execute(
            select(
                models.Player.hashed_password,
            ).where(models.Player.name == data["name"])
        )
        db.close()  # close the conn asap
        result = None
        for row in hashed:
            result = row.hashed_password
        if result is None:
            await connection_manager.send_to_client(
                f"No account with that username found {row._asdict()}",
                websocket,
            )
        if bcrypt.checkpw(data["password"].encode("utf-8"), result.encode("utf-8")):
            self.certificated |= {client_id: (data["name"], websocket)}
            await connection_manager.send_to_client(
                f"Welcome, {data['name']}!", websocket
            )
        else:
            await connection_manager.send_to_client(
                "Login failed, incorrect username or password", websocket
            )

    async def new_account(self, data, client_id, connection_manager, websocket):
        """
        Account creation request

        JSON Structure:
        {
            "action": "new_account"
            "name": "xxx"
            "password": "xxx"
        }
        """
        if client_id in self.certificated.keys():
            await connection_manager.send_to_client(
                "You are already logged in", websocket
            )
            return
        db = database.SessionLocal()
        try:
            db.execute(
                insert(models.Player).values(
                    name=data["name"],
                    hashed_password=bcrypt.hashpw(
                        data["password"].encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8"),
                )
            )
            db.commit()
            db.close()  # close the conn asap
        except IntegrityError:
            await connection_manager.send_to_client(
                f"Username \"{data['name']}\" taken", websocket
            )
            return
        self.certificated |= {client_id: (data["name"], websocket)}
        await connection_manager.send_to_client(
            f"New account created, welcome, {data['name']}!", websocket
        )

    async def query_online_users(self, data, client_id, connection_manager, websocket):
        """
        Returns online users

        JSON Structure:
        {
            "action": "query_online_users"
        }
        """
        await connection_manager.send_to_client(
            ", ".join(
                vals[0] for vals in self.certificated.values())
            ), websocket
        )

    async def go_hunting(self, data, client_id, connection_manager, websocket):
        """
        Go out into the wild and seek out monsters to fight

        JSON Structure:
        {
            "action": "go_hunting"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def challenge_player(self, data, client_id, connection_manager, websocket):
        """
        Challenge another player to a fight

        JSON Structure:
        {
            "action": "challenge_player"
            "player": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def accept_challenge(self, data, client_id, connection_manager, websocket):
        """
        Accept an incoming challenge

        JSON Structure:
        {
            "action": "accept_challenge"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def attack(self, data, client_id, connection_manager, websocket):
        """
        Choose an attack to use in the current fight

        JSON Structure:
        {
            "action": "attack"
            "attack": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def view_shop(self, data, client_id, connection_manager, websocket):
        """
        Look at available shop items

        JSON Structure:
        {
            "action": "view_shop"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def buy(self, data, client_id, connection_manager, websocket):
        """
        Buy an item from the shop

        JSON Structure:
        {
            "action": "buy"
            "item": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def sell(self, data, client_id, connection_manager, websocket):
        """
        Sell an item for gold

        JSON Structure:
        {
            "action": "sell"
            "item": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def seek_quest(self, data, client_id, connection_manager, websocket):
        """
        Look up available quests

        JSON Structure:
        {
            "action": "seek_quest"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def accept_quest(self, data, client_id, connection_manager, websocket):
        """
        Take on a quest

        JSON Structure:
        {
            "action": "accept_quest"
            "quest": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def fulfil_quest(self, data, client_id, connection_manager, websocket):
        """
        Report back on a completed quest to collect your reward

        JSON Structure:
        {
            "action": "fulfil_quest"
            "quest": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def inventory(self, data, client_id, connection_manager, websocket):
        """
        Look at the contents of your bag

        JSON Structure:
        {
            "action": "inventory"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def equip(self, data, client_id, connection_manager, websocket):
        """
        Equip an item

        JSON Structure:
        {
            "action": "equip"
            "item": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def use_item(self, data, client_id, connection_manager, websocket):
        """
        Use a consumable item

        JSON Structure:
        {
            "action": "use_item"
            "item": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def status(self, data, client_id, connection_manager, websocket):
        """
        Check your health, mana, progress on current quests and other details

        JSON Structure:
        {
            "action": "status"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def send_trade_offer(self, data, client_id, connection_manager, websocket):
        """
        Offer to initiate a trade with another user

        JSON Structure:
        {
            "action": "send_trade_offer"
            "user": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def put_trade(self, data, client_id, connection_manager, websocket):
        """
        Set the items and gold offered in current trade

        JSON Structure:
        {
            "action": "put_trade"
            "items": [id1, id2]
            "gold": 123
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def accept_trade(self, data, client_id, connection_manager, websocket):
        """
        Accept the terms of trade. Items will be exchanged when both players accept

        JSON Structure:
        {
            "action": "accept_trade"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    async def chat(self, data, client_id, connection_manager, websocket):
        """
        Send a chat message to all users

        JSON Structure:
        {
            "action": "chat"
            "message": "xxx"
        }
        """
        await connection_manager.broadcast(
            f"[Chat] {self.certificated[client_id][0]}: {data['message']}", websocket
        )

    async def direct_message(self, data, client_id, connection_manager, websocket):
        """
        Send a message to another user

        JSON Structure:
        {
            "action": "direct_message"
            "message": "xxx"
            "user": "xxx"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)
