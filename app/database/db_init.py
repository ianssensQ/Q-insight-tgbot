from app.infrastructure.database.database import Base, engine
from app.infrastructure.models_tables.usertable import UserTable


# from app.infrastructure.models_tables.balance import BalanceTable
# from app.infrastructure.models_tables.transactions import TransactionHistory
# from app.infrastructure.models_tables.data import RequestTable


def init_db():
    Base.metadata.create_all(bind=engine)


def drop_db():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    drop_db()
    init_db()
