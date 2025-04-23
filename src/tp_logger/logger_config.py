import logging
import os

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger



# 示例使用
if __name__ == "__main__":
    logger = get_logger()
    logger.debug('这是一条调试级别的日志')
    logger.info('这是一条信息级别的日志')
    logger.warning('这是一条警告级别的日志')
    logger.error('这是一条错误级别的日志')
    logger.critical('这是一条严重错误级别的日志')    