import time
import uuid

import bcrypt
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from . import database, models
from .fight import PVEFight, PVPFight
from .skills.strike import Strike


def login_required(func):
    """When decorator used login will be required on the action specified"""

    async def wrapper(self, data, client_id, connection_manager, websocket):
        if client_id in self.certed.id_name:
            return await func(self, data, client_id, connection_manager, websocket)
        else:
            await connection_manager.send_to_client(
                "Login to use the action", websocket
            )

    return wrapper


class Certificated:
    """Certificating login/new_account creates certificate"""

    id_name = {}
    name_ws = {}

    def add(self, client_id, name, websocket):
        """Add user"""
        self.id_name |= {client_id: name}
        self.name_ws |= {name: websocket}

    def delete(self, client_id):
        """Delete user"""
        if client_id in self.id_name:
            name = self.id_name.pop(client_id)
            self.name_ws.pop(name)


class Sessions:
    """Track temporary sessions for users"""

    fights = {}

    def add_pve_fight(self, player):
        """Begin tracking a PVE fight"""
        if self.is_fighting(player.name):
            return
        self.fights[player.name] = PVEFight(player)

    def add_pvp_fight(self, offender, defender):
        """Begin tracking a PVP fight"""
        if self.is_fighting(offender.name):
            return
        self.fights[offender.name] = PVPFight(offender, defender)

    def is_fighting(self, name):
        """Check if a user is in a fight"""
        return name in self.fights

    def attack(self, player_name, skill, websocket):
        """Run a turn of combat"""
        result = self.fights[player_name].use_skill(skill)

        if result[1] != 0:
            # TODO: Propagate updated player data back to database
            self.fights[player_name].pop()
        return result[0]


class RunningPVPs:
    """PVP tracking"""

    lobby = []
    offender_id = {}
    defender_id = {}
    countdown = {}


class ActionManager:
    """Handling actions from client"""

    certed = Certificated()
    running_pvps = RunningPVPs()
    sessions = Sessions()
    pvp_sessions = {}

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
                f"No account with username {data['name']} found",
                websocket,
            )
        if bcrypt.checkpw(data["password"].encode("utf-8"), result.encode("utf-8")):
            self.certed.add(client_id, data["name"], websocket)
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
        if client_id in self.certed.id_name.keys():
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
        self.certed.add(client_id, data["name"], websocket)
        await connection_manager.send_to_client(
            f"New account created, welcome, {data['name']}!", websocket
        )

    @login_required
    async def query_online_users(self, data, client_id, connection_manager, websocket):
        """
        Returns online users

        JSON Structure:
        {
            "action": "query_online_users"
        }
        """
        await connection_manager.send_to_client(
            ", ".join(self.certed.id_name.values()), websocket
        )

    @login_required
    async def go_hunting(self, data, client_id, connection_manager, websocket):
        """
        Go out into the wild and seek out monsters to fight

        JSON Structure:
        {
            "action": "go_hunting"
        }
        """
        db = database.SessionLocal()
        player = db.execute(
            models.Player.select().where(
                models.Player.name == self.certed.id_name[client_id]
            )
        ).fetchone()
        db.close()
        if self.sessions.is_fighting(player.name):
            await connection_manager.send_to_client(
                "You are already in a fight!", websocket
            )
        else:
            self.sessions.add_pve_fight(player)
            # TODO: make this more descriptive
            await connection_manager.send_to_client("Now fighting!", websocket)

    @login_required
    async def challenge_player(self, data, client_id, connection_manager, websocket):
        """
        Challenge another player to a fight

        JSON Structure:
        {
            "action": "challenge_player"
            "player": "xxx"
        }
        """
        lobby = uuid.uuid4()
        self.pvp_intermission.lobby.append(lobby)
        self.pvp_intermission.client_id |= {lobby: client_id}
        self.pvp_intermission.countdown |= {lobby: time.time() + 30}
        await connection_manager.send_to_client(
            f"Challenge from {self.certed.id_name[client_id]}. Lobby ID: {lobby}",
            self.certed.name_ws[data["player"]],
        )
        await connection_manager.send_to_client(
            "Challenge sent",
            websocket,
        )

    @login_required
    async def accept_challenge(self, data, client_id, connection_manager, websocket):
        """
        Accept an incoming challenge

        JSON Structure:
        {
            "action": "accept_challenge"
            "lobby": "xxx"
        }
        """
        lobby = data["lobby"]
        pvp_inter = self.pvp_intermission
        if lobby in pvp_inter.lobby:
            if client_id == pvp_inter.defender_id[lobby]:
                if time.time() <= pvp_inter.countdown[lobby]:
                    db = database.SessionLocal()
                    offender = db.execute(
                        models.Player.select().where(
                            models.Player.name == pvp_inter.offender_id[lobby]
                        )
                    ).fetchone()
                    defender = db.execute(
                        models.Player.select().where(
                            models.Player.name == pvp_inter.defender_id[lobby]
                        )
                    ).fetchone()
                    db.close()
                    if self.sessions.is_fighting(defender.name):
                        await connection_manager.send_to_client(
                            "You are already in a fight!", websocket
                        )
                    else:
                        self.sessions.add_pvp_fight(offender, defender)
                        # TODO: make this more descriptive
                        await connection_manager.send_to_client(
                            "Now fighting!", websocket
                        )
                else:
                    await connection_manager.send_to_client(
                        "Time reached!",
                        websocket,
                    )
            else:
                await connection_manager.send_to_client(
                    "You're not the player for the lobby!",
                    websocket,
                )
        else:
            await connection_manager.send_to_client(
                "Invalid lobby ID!",
                websocket,
            )

    @login_required
    async def attack(self, data, client_id, connection_manager, websocket):
        """
        Choose an attack to use in the current fight

        JSON Structure:
        {
            "action": "attack"
            "attack": "xxx"
        }
        """
        # For now, the only attack the player knows is strike.
        # TODO: Add skill picking
        self.sessions.attack(self.certed.id_name[client_id], Strike, websocket)

    @login_required
    async def view_shop(self, data, client_id, connection_manager, websocket):
        """
        Look at available shop items

        JSON Structure:
        {
            "action": "view_shop"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    @login_required
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

    @login_required
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

    @login_required
    async def seek_quest(self, data, client_id, connection_manager, websocket):
        """
        Look up available quests

        JSON Structure:
        {
            "action": "seek_quest"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    @login_required
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

    @login_required
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

    @login_required
    async def inventory(self, data, client_id, connection_manager, websocket):
        """
        Look at the contents of your bag

        JSON Structure:
        {
            "action": "inventory"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    @login_required
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

    @login_required
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

    @login_required
    async def status(self, data, client_id, connection_manager, websocket):
        """
        Check your health, mana, progress on current quests and other details

        JSON Structure:
        {
            "action": "status"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    @login_required
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

    @login_required
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

    @login_required
    async def accept_trade(self, data, client_id, connection_manager, websocket):
        """
        Accept the terms of trade. Items will be exchanged when both players accept

        JSON Structure:
        {
            "action": "accept_trade"
        }
        """
        await connection_manager.send_to_client("Not yet implemented", websocket)

    @login_required
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
            f"[Chat] {self.certed.id_name[client_id]}: {data['message']}"
        )

    @login_required
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
        await connection_manager.send_to_client(
            f"[DM] {self.certed.id_name[client_id]}: {data['message']}",
            self.certed.name_ws[data["user"]],
        )
