import os
from playhouse.sqlite_ext import *
from datetime import datetime
from chan_agent.logger import logger

# 数据库文件路径
db_path = 'logs/db.sqlite'

# 确保目录存在
os.makedirs(os.path.dirname(db_path), exist_ok=True)

db = SqliteDatabase(db_path)


class LLMTracker(Model):
    id = AutoField()        # 自动递增主键
    data = JSONField()      # JSON 格式的字段
    created_at = DateTimeField(default=datetime.now)  # 自动记录创建时间

    class Meta:
        database = db
        table_name = 'llm_tracker'

    @classmethod
    def initialize_table(cls):
        """
        检查表是否存在，不存在时自动创建。
        """
        if not db.table_exists(cls._meta.table_name):
            db.create_tables([cls])
            logger.info(f"Table '{cls._meta.table_name}' created successfully.")

    @classmethod
    def create_log(cls, data: dict):
        """
        写入一条新数据到 LLMTracker 表。
        
        Args:
            data (dict): 字典数据。

        Returns:
            LLMTracker: 返回插入的记录对象。
        """
        try:
            cls.initialize_table()
            with db.atomic():  # 启用事务
                new_record = cls.create(data=data)
            return new_record
        except Exception as e:
            raise ValueError(f"Failed to write data to LLMTracker: {e}")
    

def llm_log(data: dict):
    LLMTracker.create_log(data)
