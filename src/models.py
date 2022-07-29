from sqlalchemy import JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base, engine


class Player(Base):
    """Player in ORM"""

    __tablename__ = "players"

    UUID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(32), unique=True, index=True)
    hashed_password = Column(String(72))
    role = Column(String, index=True)
    hp = Column(Integer)
    max_hp = Column(Integer)
    energy = Column(Integer)
    max_energy = Column(Integer)
    gold = Column(Integer)
    pve_cooldown = Column(TIMESTAMP)
    pvp_cooldown = Column(TIMESTAMP)


class Item(Base):
    """Item in ORM"""

    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String, index=True)
    item_type = Column(String)
    equipped = Column(Boolean)
    amount = Column(Integer)
    item_info = Column(JSON)
    owner = Column(Integer, ForeignKey("players.UUID"), index=True)

    players = relationship("Player")


Base.metadata.create_all(engine)
