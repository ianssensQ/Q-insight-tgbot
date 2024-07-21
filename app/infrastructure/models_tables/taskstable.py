from app.infrastructure.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from app.infrastructure.models_tables.usertable import UserTable


class TaskTable(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.tg_id'))
    tg_tasked_channels = Column(ARRAY(String))
    interval = Column(Integer)  # in days

    posts_count = Column(Integer)
    summ_result = Column(ARRAY(String))

