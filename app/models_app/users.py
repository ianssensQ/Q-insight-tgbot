# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.models_tables.usertable import UserTable


class User:
    def __init__(self, user_id="", tg_id=0, tg_channels=None):
        if tg_channels is None:
            tg_channels = []
        self.id = user_id
        self.tg_id = tg_id
        self.tg_channels = tg_channels

    def __repr__(self):
        return (f"User(id={self.id},"
                f" tg_id={self.tg_id},"
                f"tg_channels={self.tg_channels})")

    def create_user(self):
        with SessionLocal() as db:
            user = UserTable(tg_id=self.tg_id, tg_channels=self.tg_channels)
            db.add(user)
            db.commit()
            self.id = user.id


if __name__ == "__main__":
    user = User(2, 1223, ["Ivanov", "alexey@ya.ru", "12345"])
    user.create_user()

