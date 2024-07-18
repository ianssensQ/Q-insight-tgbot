from app.infrastructure.database.database import Base, engine
from app.infrastructure.models_tables.usertable import UserTable
from app.infrastructure.models_tables.taskstable import TaskTable
from app.infrastructure.models_tables.channelstable import ChannelTable
from app.infrastructure.models_tables.poststable import PostTable


def init_db():
    Base.metadata.create_all(bind=engine)


def drop_db():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    drop_db()
    init_db()
