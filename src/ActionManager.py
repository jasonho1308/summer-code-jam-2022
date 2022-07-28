import bcrypt
from sqlalchemy import select

from . import database, models


class ActionManager:
    """Handling actions from client"""

    certificated = []

    def login(self, data, client_id):
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
            select(models.Player.hashed_password).where(models.Player.name == data["name"])
        )
        if bcrypt.checkpw(data["password"], hashed):
            self.certificated.append(client_id)
        db.close()
