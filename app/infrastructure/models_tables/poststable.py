from app.infrastructure.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from app.infrastructure.models_tables.taskstable import TaskTable
from app.infrastructure.models_tables.channelstable import ChannelTable


class PostTable(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))

    post_text = Column(String)
    post_url = Column(String)
    post_date = Column(String)

    class_ = Column(Integer)

    summ_post_result = Column(String)
