from app.infrastructure.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from app.infrastructure.models_tables.taskstable import TaskTable


class ChannelTable(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    tg_channel_name = Column(String)
    interval = Column(Integer)  # in days

    posts_count = Column(Integer)
    summ_channel_result = Column(String)
