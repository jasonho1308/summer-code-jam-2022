from sqlalchemy import (
    JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
)
from sqlalchemy.orm import relationship

from .database import Base, engine


class Player(Base):
    """Player in ORM"""

    __tablename__ = "players"

    name = Column(String(32), primary_key=True, index=True)
    hashed_password = Column(String(72))
    role = Column(String, index=True)
    hp = Column(Integer, index=True)
    max_hp = Column(Integer, index=True)
    energy = Column(Integer, index=True)
    max_energy = Column(Integer, index=True)
    pve_cooldown = Column(TIMESTAMP, index=True)
    pvp_cooldown = Column(TIMESTAMP, index=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    """Item in ORM"""

    __tablename__ = "items"

    item_type = Column(String, index=True)
    title = Column(String, index=True)
    equipped = Column(Boolean, index=True)
    amount = Column(Integer, index=True)
    item_info = Column(JSON, index=True)
    owner_name = Column(Integer, ForeignKey("players.name"))

    owner = relationship("User", back_populates="items")


Base.metadata.create_all(engine)
