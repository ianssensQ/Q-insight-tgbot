from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
from contextlib import contextmanager

SQL_CONNECTION = config("DATABASE_URL")
engine = create_engine(SQL_CONNECTION)
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
    print('0000')
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