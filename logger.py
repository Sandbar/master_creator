from pythonjsonlogger import jsonlogger
from datetime import datetime
import logging
import sys
import time
import pytz

tz = pytz.timezone('Asia/Shanghai')


class StackJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(StackJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai'))
        log_record['severity'] = log_record['levelname']
        if log_record.get('levelname') and log_record.get('severity'):
            del log_record['levelname']


# add fields you want to use, add severity fields for stack_driver
formatter = StackJsonFormatter('(timestamp) (severity) (levelname) (message)')


# handler filter
def stderr_filter(record):
    if record.levelno >= logging.WARNING:
        return True
    return False


def stdout_filter(record):
    if logging.WARNING > record.levelno >= logging.DEBUG:
        return True
    return False


stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.addFilter(stdout_filter)
stdout_handler.setFormatter(formatter)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.addFilter(stderr_filter)
stderr_handler.setFormatter(formatter)
