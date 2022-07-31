import time
import uuid
from typing import Optional

import bcrypt
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from src.shop import Shop

from . import database
from .fight import PVEFight, PVPFight
from .models import Player
from .skills import skills


def login_required(func):
    """When decorator used login will be required on the action specified"""

    async def wrapper(self, data, client_id, connection_manager, websocket):
        if client_id in self.certed.id_name:
            return await func(self, data, client_id, connection_manager, websocket)
        else:
            await connection_manager.send_to_client("Login to use the action", websocket)

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

    def get_fight(self, player) -> Optional[PVEFight | PVPFight]:
        """Get current fight for player, if exists"""
        return self.fights.get(player.name)

    def is_fighting(self, name):
        """Check if a user is in a fight"""
        return name in self.fights

    def get_status(self, name):
        """Get the status of both combatants"""
        fight = self.fights[name]
        # TODO: Case for PVP
        player = fight.player
        monster = fight.monster
        output = f"{player.name} - HP:{player.hp}/{player.max_hp} - Energy:{player.energy}/{player.max_energy}"
        output += f"\n{monster.name} - HP:{monster.hp}/{monster.max_hp} - Energy:{monster.energy}/{monster.max_energy}"
        return output

    def attack(self, player_name, skill, websocket):
        """Run a turn of combat"""
        fight = self.fights[player_name]
        player = fight.player
        result = fight.use_skill(skill)

        if result[1] != 0:
            if isinstance(fight, PVEFight):
                with database.SessionLocal() as db:
                    db.query(Player).filter(Player.name == player_name).update(
                        {
                            "level": player.level,
                            "experience": player.experience,
                            "hp": player.hp,
                            "max_hp": player.max_hp,
                            "energy": player.energy,
                            "max_energy": player.max_energy,
                            "strength": player.strength,
                            "intelligence": player.intelligence,
                            "stamina": player.stamina,
                            "dexterity": player.dexterity,
                            "charisma": player.charisma,
                            "gold": player.gold,
                        }
                    )
                    db.commit()
            else:
                defender: Player = fight.defender
                offender: Player = fight.offender
                with database.SessionLocal() as db:
                    db.query(Player).filter(Player.name == defender.name).update(
                        {
                            "level": defender.level,
                            "experience": defender.experience,
                            "hp": defender.hp,
                            "max_hp": defender.max_hp,
                            "energy": defender.energy,
                            "strength": defender.strength,
                            "intelligence": defender.intelligence,
                            "stamina": defender.stamina,
                            "dexterity": defender.dexterity,
                            "charisma": defender.charisma,
                            "gold": defender.gold,
                        }
                    )
                    db.query(Player).filter(Player.name == offender.name).update(
                        {
                            "level": offender.level,
                            "experience": offender.experience,
                            "hp": offender.hp,
                            "max_hp": offender.max_hp,
                            "energy": offender.energy,
                            "strength": offender.strength,
                            "intelligence": offender.intelligence,
                            "stamina": offender.stamina,
                            "dexterity": offender.dexterity,
                            "charisma": offender.charisma,
                            "gold": offender.gold,
                        }
                    )
                    db.commit()
            self.fights.pop(player_name)
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
    shop = Shop()
    pvp_sessions = {}

    def get_player_with_client_id(self, client_id):
        """Get a Player object from a client id"""
        with database.SessionLocal() as db:
            return db.query(Player).filter_by(name=self.certed.id_name[client_id]).one()

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
        with database.SessionLocal() as db:
            hashed = db.execute(
                select(Player.hashed_password,).where(Player.name == data["name"])
            )
        result = None
        for row in hashed:
            result = row.hashed_password
        if client_id in self.certed.id_name.keys():
            await connection_manager.send_to_client("Already logged in", websocket)
            return
        if result is None:
            await connection_manager.send_to_client(
                f"No account with username {data['name']} found", websocket
            )
        elif bcrypt.checkpw(data["password"].encode("utf-8"), result.encode("utf-8")):
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
        with database.SessionLocal() as db:
            try:
                db.execute(
                    insert(Player).values(
                        name=data["name"],
                        hashed_password=bcrypt.hashpw(
                            data["password"].encode("utf-8"), bcrypt.gensalt()
                        ).decode("utf-8"),
                    )
                )
                db.commit()
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
        player = self.get_player_with_client_id(client_id)

        if curr_fight := self.sessions.get_fight(player):
            message = "You are already in a fight with "
            if isinstance(curr_fight, PVEFight):
                message += f"a {curr_fight.monster.name}!"
            elif isinstance(curr_fight, PVPFight):
                opponent = [user for user in (curr_fight.offender, curr_fight.defender)
                            if user.name != player.name][0]
                message += f"user {opponent.name}!"
            await connection_manager.send_to_client(message, websocket)
        else:
            new_fight = PVEFight(player)
            self.sessions.fights[player.name] = new_fight
            await connection_manager.send_to_client(
                f"You come accross a wild {new_fight.monster.name}...FIGHT!", websocket
            )

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
                    with database.SessionLocal() as db:
                        offender = db.query(Player).filter_by(name=pvp_inter.offender_id[lobby]).one()
                        defender = db.query(Player).filter_by(name=pvp_inter.defender_id[lobby]).one()
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
                        "Time reached!", websocket,
                    )
            else:
                await connection_manager.send_to_client(
                    "You're not the player for the lobby!", websocket,
                )
        else:
            await connection_manager.send_to_client(
                "Invalid lobby ID!", websocket,
            )

    @login_required
    async def attack(self, data, client_id, connection_manager, websocket):
        """
        Choose an attack to use in the current fight

        JSON Structure:
        {
            "action": "attack"
            "skill": "xxx"
        }
        """
        if "skill" not in data.keys():
            await connection_manager.send_to_client(
                "Please provide a skills", websocket
            )
            return
        if not self.sessions.is_fighting(self.certed.id_name[client_id]):
            await connection_manager.send_to_client(
                "You aren't fighting anything", websocket,
            )
            return
        player = self.get_player_with_client_id(client_id)

        skill = skills.get(data["skill"].casefold())
        if skill is None:
            await connection_manager.send_to_client(
                "Skill doesn't exist", websocket,
            )
            return
        if not skill.learnt(player):
            await connection_manager.send_to_client(
                "Skill not learnt", websocket,
            )
        if skill:
            await connection_manager.send_to_client(
                self.sessions.attack(self.certed.id_name[client_id], skill, websocket), websocket,
            )

    @login_required
    async def fight_status(self, data, client_id, connection_manager, websocket):
        """
        Check yours and your opponent's status

        JSON Structure:
        {
            "action": "fight_status"
        }
        """
        if not self.sessions.is_fighting(self.certed.id_name[client_id]):
            await connection_manager.send_to_client(
                "You aren't fighting anything", websocket,
            )
            return
        await connection_manager.send_to_client(self.sessions.get_status(self.certed.id_name[client_id]), websocket)

    @login_required
    async def list_skills(self, data, client_id, connection_manager, websocket):
        """List the player's current list of learned skills"""
        player = self.get_player_with_client_id(client_id)
        learned_skills = [repr(skill.name) for skill in skills.values() if skill.learnt(player)]
        await connection_manager.send_to_client(
            "\n".join(learned_skills), websocket
        )

    @login_required
    async def view_shop(self, data, client_id, connection_manager, websocket):
        """
        Look at available shop items

        JSON Structure:
        {
            "action": "view_shop"
        }
        """
        await connection_manager.send_to_client(
            self.shop.display_shop(), websocket
        )

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
        message = self.shop.buy(data["item"], self.get_player_with_client_id(client_id))
        await connection_manager.send_to_client(message, websocket)

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
    async def view_status(self, data, client_id, connection_manager, websocket):
        """
        Check your health, mana, progress on current quests and other details

        JSON Structure:
        {
            "action": "view_status"
        }
        """
        player = self.get_player_with_client_id(client_id)
        player_data = [
            f"name: {player.name}",
            f"level: {player.level}",
            f"exp: {player.experience}",
            f"gold: {player.gold}",
            f"hp: {player.hp}/{player.max_hp}",
            f"energy: {player.energy}/{player.max_energy}",
        ]
        await connection_manager.send_to_client("\n".join(player_data), websocket)

    @login_required
    async def view_status_full(self, data, client_id, connection_manager, websocket):
        """
        Check your health, mana, progress on current quests and other details

        JSON Structure:
        {
            "action": "view_status_full"
        }
        """
        player = self.get_player_with_client_id(client_id)
        player_data = [
            f"name: {player.name}",
            f"level: {player.level}",
            f"exp: {player.experience}",
            f"gold: {player.gold}",
            f"hp: {player.hp}/{player.max_hp}",
            f"energy: {player.energy}/{player.max_energy}",
            f"strength: {player.strength}",
            f"intelligence: {player.intelligence}",
            f"dexterity: {player.dexterity}",
            f"stamina: {player.stamina}",
            f"charisma: {player.charisma}",
        ]
        await connection_manager.send_to_client("\n".join(player_data), websocket)

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
