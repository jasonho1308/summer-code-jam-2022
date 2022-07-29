import bcrypt
from sqlalchemy import select

from . import database, models


class ActionManager:
    """Handling actions from client"""

    certificated = []

    def login(self, data, client_id, connection_manager, websocket):
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
            connection_manager.send_to_client("Welcome!")
        else:
            connection_manager.send_to_client(
                "Login failed, incorrect username or password"
            )
