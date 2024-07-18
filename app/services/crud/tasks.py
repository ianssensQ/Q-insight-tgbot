# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.models_tables.taskstable import TaskTable
from loguru import logger


class Task:
    def __init__(self, task_id="", user_id="",
                 tg_tasked_channels=None, interval=""):
        if tg_tasked_channels is None:
            tg_tasked_channels = []
        self.id = task_id
        self.user_id = user_id
        self.tg_tasked_channels = tg_tasked_channels
        self.interval = interval

    def __repr__(self):
        return (f"Task <(id={self.id},"
                f" user_id={self.user_id},"
                f"tg_channels={self.tg_tasked_channels},"
                f"interval={self.interval})>")

    def create_task(self):
        with SessionLocal() as db:
            task = TaskTable(user_id=self.user_id,
                             tg_tasked_channels=self.tg_tasked_channels,
                             interval=self.interval)
            db.add(task)
            db.commit()
            self.id = task.id

            logger.info(f"Task saved: {task}")

    def save_task_result(self, posts_count, summ_result):
        with SessionLocal() as db:
            task = db.query(TaskTable).filter(TaskTable.id == self.id).first()
            task.posts_count = posts_count
            task.summ_result = summ_result
            db.commit()
            db.refresh(task)

            logger.info(f"Task result saved: {task}")

    def check_res(self):
        if self.load_task_result()[0] is None:
            logger.info(f"Request not found: {self}")
            return False
        else:
            return True

    def load_task_result(self):
        with SessionLocal() as db:
            task = db.query(TaskTable.summ_result).filter(TaskTable.id == self.id).first()
            logger.info(f"Request loaded: {task}")
            return task


if __name__ == "__main__":
    task = Task(1, 1, ["Ivanov", "alexey@ya.ru", "12345"], 1)
    task.create_task()
    # print(task.check_res())
    # print(task.load_task_result())
    task.save_task_result(1, "test")
    # print(task.check_res())
