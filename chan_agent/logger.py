import logging  

# 创建一个日志记录器  
logger = logging.getLogger()  
logger.setLevel(logging.INFO)  # 设置日志级别为 DEBUG  

# 设置控制台处理器  
console_handler = logging.StreamHandler()  
console_handler.setLevel(logging.INFO)  # 控制台日志级别  

# 设置日志格式  
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
console_handler.setFormatter(formatter)  

# 添加处理器到日志记录器  
logger.addHandler(console_handler)