from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
from contextlib import contextmanager

SQL_CONNECTION = config("DATABASE_URL")
SELECTL_DB = config("SELECTL_DB")

engine = create_engine(SELECTL_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session():
    try:
        with SessionLocal() as session:
            yield session
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()


Base = declarative_base()

if __name__ == "__main__":

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Попробуйте подключиться к базе данных
        connection = engine.connect()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        # Закройте соединение
        print('no')
        connection.close()
        session.close()