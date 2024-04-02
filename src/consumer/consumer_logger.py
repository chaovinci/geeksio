import logging
import os

# 创建logger
logger = logging.getLogger('consumer')
logger.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG

# 如果日志目录不存在，创建它
log_directory = "/root/logs"
os.makedirs(log_directory, exist_ok=True)

# 创建一个handler，用于写入日志文件
file_handler = logging.FileHandler(f'{log_directory}/consumer.log')
file_handler.setLevel(logging.DEBUG)  # 设置日志级别

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)


# 给logger添加handler
logger.addHandler(file_handler)
