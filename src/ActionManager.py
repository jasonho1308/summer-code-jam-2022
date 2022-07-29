import bcrypt
from sqlalchemy import insert, select

from . import database, models


class ActionManager:
    """Handling actions from client"""

    certificated = []

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
            select(models.Player.hashed_password).where(
                models.Player.name == data["name"]
            )
        )
        db.close()  # close the conn asap
        if bcrypt.checkpw(data["password"].encode("utf-8"), hashed):
            self.certificated.append(client_id)
            await connection_manager.send_to_client("Welcome!", websocket)
        else:
            await connection_manager.send_to_client(
                "Login failed, incorrect username or password", websocket
            )

    async def new_account(self, data, client_id, connection_manager, websocket):
        """
        Account creation request

        JSON Structure:
        {
            "action": "create_account"
            "name": "xxx"
            "password": "xxx"
        }
        """
        if client_id in self.certificated:
            await connection_manager.send_to_client(
                "You are already logged in", websocket
            )
            return
        db = database.SessionLocal()
        db.execute(
            insert(models.Player).values(
                name=data["name"],
                hashed_password=bcrypt.hashpw(
                    data["password"].encode("utf-8"), bcrypt.gensalt()
                ),
            )
        )
        db.close()  # close the conn asap
        self.certificated.append(client_id)
        await connection_manager.send_to_client(
            f"New account created, welcome, {data['name']}!", websocket
        )
