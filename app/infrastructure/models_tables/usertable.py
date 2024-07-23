from app.infrastructure.database.database import Base
from sqlalchemy import Column, Integer, ARRAY, String


class UserTable(Base):
    __tablename__ = "users"
    tg_id = Column(Integer, primary_key=True)
    tg_trackable_channels = Column(ARRAY(String))

