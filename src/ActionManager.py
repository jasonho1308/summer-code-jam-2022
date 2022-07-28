import bcrypt
from sqlalchemy import select

from . import database, models


class ActionManager:
    certificated = []

    def login(self, data, client_id):
        db = database.SessionLocal()
        hashed = db.execute(
            select(models.Player.hashed_password).where(Player.name == data["name"])
        )
        if bcrypt.checkpw(passwd, hashed):
            self.certificated.append(client_id)
        db.close()
