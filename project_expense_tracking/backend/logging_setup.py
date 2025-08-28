import logging


def setup_Logger(name,log_file="server_check.log",level=logging.DEBUG):

    #Create a custom logger
    logger=logging.getLogger('db_helper')

    #Configure the custom logger

    logger.setLevel(level)
    file_hander=logging.FileHandler('log_file')
    formatter=logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s')
    file_hander.setFormatter(formatter)
    logger.addHandler(file_hander)

    return logger