from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String

from .database import Base, engine


class Player(Base):
    """Player in ORM"""

    __tablename__ = "players"

    UUID = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(32), unique=True, index=True)
    hashed_password = Column(String(72))
    admin = Column(Boolean)

    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    energy = Column(Integer, default=25)
    max_energy = Column(Integer, default=25)
    strength = Column(Integer, default=5)
    intelligence = Column(Integer, default=5)
    dexterity = Column(Integer, default=5)
    stamina = Column(Integer, default=5)
    charisma = Column(Integer, default=5)

    gold = Column(Integer, default=0)
    pve_cooldown = Column(TIMESTAMP)
    pvp_cooldown = Column(TIMESTAMP)


Base.metadata.create_all(engine)
