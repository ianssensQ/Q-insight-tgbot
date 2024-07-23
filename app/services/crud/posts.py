# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.models_tables.taskstable import TaskTable
from app.infrastructure.models_tables.channelstable import ChannelTable
from app.infrastructure.models_tables.poststable import PostTable
from loguru import logger


class Post:
    def __init__(self, post_id="", task_id="", channel_id=""):
        self.id = post_id
        self.task_id = task_id
        self.channel_id = channel_id

    def __repr__(self):
        return (f"Post <(id={self.id},"
                f" task_id={self.task_id},"
                f"channel_id={self.channel_id})>")

    @staticmethod
    def get_ids(task_id, channel_id):
        with SessionLocal() as db:
            ids = db.query(PostTable.id).filter(PostTable.task_id == task_id,
                                                PostTable.channel_id == channel_id).all()
            logger.info(f"Post ids loaded: {ids}")
            return ids

    def get_text_from_post(self):
        with SessionLocal() as db:
            text = db.query(PostTable.post_text).filter(PostTable.id == self.id).first()
            logger.info(f"Text loaded: {text}")
            return text

    @staticmethod
    def filter_posts(task_id, channel_id):
        with SessionLocal() as db:
            ids = db.query(PostTable.id).filter(PostTable.task_id == task_id,
                                                PostTable.channel_id == channel_id,
                                                PostTable.class_ != 0,
                                                ).all()
            logger.info(f"Text loaded: {ids}")
            return ids

    def save_post_result_class(self, class_):
        with SessionLocal() as db:
            post = db.query(PostTable).filter(PostTable.id == self.id).first()
            post.class_ = class_
            db.commit()
            db.refresh(post)

            logger.info(f"Post class result saved: {post}")

    def check_res_class(self):
        if self.load_post_result_class()[0] is None:
            logger.info(f"Request not found: {self}")
            return False
        else:
            return True

    def load_post_result_class(self):
        with SessionLocal() as db:
            post = db.query(PostTable.class_).filter(PostTable.id == self.id).first()
            logger.info(f"Request loaded: {post}")
            return post

    def save_post_result_summ(self, summ_post_result):
        with SessionLocal() as db:
            post = db.query(PostTable).filter(PostTable.id == self.id).first()
            post.summ_post_result = summ_post_result
            db.commit()
            db.refresh(post)

            logger.info(f"Post summ result saved: {post}")

    def check_res_summ(self):
        if self.load_post_result_summ()[0] is None:
            logger.info(f"Request not found: {self}")
            return False
        else:
            return True

    def load_post_result_summ(self):
        with SessionLocal() as db:
            post = db.query(PostTable.summ_post_result).filter(PostTable.id == self.id).first()
            logger.info(f"Request loaded: {post}")
            return post


if __name__ == "__main__":
    post = Post(post_id=1250)
    if not post.check_res_class():
        print(post.get_text_from_post()[0])

    """
    while states == 'waiting for data':
        if post.get_ids(1, 2):    
            state = 'ready'
    """
