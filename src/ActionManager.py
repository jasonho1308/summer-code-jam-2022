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
            self.certificated |= {client_id: data["name"]}
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
        self.certificated |= {client_id: data["name"]}
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
            ", ".join(self.certificated.values()), websocket
        )
