# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.models_tables.taskstable import TaskTable
from app.infrastructure.models_tables.channelstable import ChannelTable
from loguru import logger


class Channel:
    def __init__(self, channel_id="", task_id="", tg_channel_name="",
                 interval=""):
        self.id = channel_id
        self.task_id = task_id
        self.tg_channel_name = tg_channel_name
        self.interval = interval

    def __repr__(self):
        return (f"Channel <(id={self.id},"
                f" task_id={self.task_id},"
                f"tg_channel_name={self.tg_channel_name},"
                f"interval={self.interval})>")

    def create_channel(self):
        with SessionLocal() as db:
            channel = ChannelTable(task_id=self.task_id,
                                   tg_channel_name=self.tg_channel_name,
                                   interval=self.interval)
            db.add(channel)
            db.commit()
            self.id = channel.id

            logger.info(f"Channel saved: {channel}")

    def find_channel(self):
        with SessionLocal() as db:
            channel = db.query(ChannelTable).filter(ChannelTable.id == self.id).first()
            logger.info(f"Channel found: {channel}")
            return channel

    def save_channel_result(self, summ_result):
        with SessionLocal() as db:
            channel = db.query(ChannelTable).filter(ChannelTable.id == self.id).first()
            channel.summ_channel_result = summ_result
            db.commit()
            db.refresh(channel)

            logger.info(f"Channel result saved: {channel}")

    def check_res(self):
        if self.load_channel_result()[0] is None:
            logger.info(f"Request not found: {self}")
            return False
        else:
            return True

    def load_channel_result(self):
        with SessionLocal() as db:
            channel = db.query(ChannelTable.summ_channel_result).filter(ChannelTable.id == self.id).first()
            logger.info(f"Request loaded: {channel}")
            return channel


if __name__ == "__main__":
    channel = Channel(1, 1, "Ivanov", 1)
    channel.create_channel()
    channel.save_channel_result("test")
