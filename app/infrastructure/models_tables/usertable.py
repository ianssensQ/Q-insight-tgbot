from app.infrastructure.database.database import Base
from sqlalchemy import Column, Integer, ARRAY, String


class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer)
    tg_channels = Column(ARRAY(String))

