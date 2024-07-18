# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.models_tables.usertable import UserTable
from loguru import logger


class User:
    def __init__(self, user_id="", tg_id="", tg_trackable_channels=None):
        if tg_trackable_channels is None:
            tg_trackable_channels = []
        self.id = user_id
        self.tg_id = tg_id
        self.tg_trackable_channels = tg_trackable_channels

    def __repr__(self):
        return (f"User(id={self.id},"
                f" tg_id={self.tg_id},"
                f"tg_channels={self.tg_trackable_channels})")

    def create_user(self):
        with SessionLocal() as db:
            user = UserTable(tg_id=self.tg_id, tg_trackable_channels=self.tg_trackable_channels)
            db.add(user)
            db.commit()
            self.id = user.id

            logger.info(f"User saved: {user}")

    def add_channels(self, new_tg_trackable_channels):
        with SessionLocal() as db:
            user = db.query(UserTable).filter(UserTable.tg_id == self.tg_id).first()
            updated_channels = user.tg_trackable_channels.copy()
            for channel in new_tg_trackable_channels:
                if channel not in updated_channels:
                    updated_channels.append(channel)

            user.tg_trackable_channels = updated_channels
            db.commit()
            db.refresh(user)

            logger.info(f"Channels added: {user}")

    def remove_channels(self, new_tg_trackable_channels):
        with SessionLocal() as db:
            user = db.query(UserTable).filter(UserTable.tg_id == self.tg_id).first()
            updated_channels = user.tg_trackable_channels.copy()
            for channel in new_tg_trackable_channels:
                if channel in updated_channels:
                    updated_channels.remove(channel)

            user.tg_trackable_channels = updated_channels
            db.commit()
            db.refresh(user)

            logger.info(f"Channels removed: {user}")

    def delete_channels(self):
        with SessionLocal() as db:
            user = db.query(UserTable).filter(UserTable.tg_id == self.tg_id).first()
            user.tg_trackable_channels = []
            db.commit()
            db.refresh(user)

            logger.info(f"User channels deleted: {user}")

    def get_tg_trackable_channels(self):
        with SessionLocal() as db:
            user = db.query(UserTable.tg_trackable_channels).filter(UserTable.tg_id == self.tg_id).first()
            logger.info(f"User channels loaded: {user}")
            return user


if __name__ == "__main__":
    user = User(1, 1221, ["Ivanov", "alexey@ya.ru", "12345"])
    user.create_user()
    # user.add_channels(["444"])
    # user.remove_channels(["Ivanov"])
    user.get_tg_trackable_channels()
    # user.delete_channels()


