import os
from loguru import logger
from pathlib import Path

CONFIG_MODULE_DIR = Path(__file__).parent.resolve()

os.environ["LOGURU_LEVEL"] = "INFO"

def get_logger(module_name:str):
    app_log = os.path.join(os.path.dirname(CONFIG_MODULE_DIR), "logs", "app.log")
    logger.add(app_log, rotation="500 MB", retention="10 days",# level="INFO",
               format="{time} | {level} | " + module_name + ":{function}:{line} - {message}")
    return logger


# def get_logger(name: str):
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)

#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.DEBUG)
#     console_handler.setFormatter(formatter)

#     log_dir = os.path.join(os.path.dirname(CONFIG_MODULE_DIR), 'logs')
#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)
#     file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
#     file_handler.setLevel(logging.INFO)
#     file_handler.setFormatter(formatter)

#     logger.addHandler(console_handler)
#     logger.addHandler(file_handler)

#     return logger

# 配置日志

# 示例使用
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.debug('这是一条调试级别的日志')
    logger.info('这是一条信息级别的日志')
    logger.warning('这是一条警告级别的日志')
    logger.error('这是一条错误级别的日志')
    logger.critical('这是一条严重错误级别的日志')    