# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.models_tables.users import UserTable


class User:
    def __init__(self, user_id="", tg_id=0):
        self.id = user_id
        self.tg_id = tg_id

    def __repr__(self):
        return (f"User(id={self.id},"
                f" tg_id={self.tg_id},")

    def create_user(self):
        with SessionLocal() as db:
            user = UserTable()
            db.add(user)
            db.commit()
            self.id = user.id
