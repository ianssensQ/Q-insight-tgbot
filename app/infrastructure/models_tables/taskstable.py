from app.infrastructure.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from app.infrastructure.models_tables.usertable import UserTable


class TaskTable(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user_tg_id = Column(Integer, ForeignKey('users.tg_id'))
    tg_tasked_channels = Column(ARRAY(String))
    interval = Column(Integer)  # in days

    summ_result = Column(ARRAY(String))

