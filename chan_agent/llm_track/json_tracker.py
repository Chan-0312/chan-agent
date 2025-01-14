import os
import datetime
import json
from filelock import FileLock 
from pathlib import Path

# 数据库文件路径
logs_dir = Path('logs')

# 确保目录存在
os.makedirs(logs_dir, exist_ok=True)

def llm_log(data: dict):
    today = datetime.date.today()
    log_path = logs_dir / f"llm_logs_{today.isoformat()}.json"
    lockfile = str(log_path) + ".lock"

    # 使用文件锁来避免并发读写冲突
    with FileLock(lockfile):
        if log_path.exists():
            # 读取现有内容
            with open(str(log_path), "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append(data)
        
        # 写入文件
        with open(str(log_path), "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)