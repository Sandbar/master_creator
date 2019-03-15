

from logger import stdout_handler, stderr_handler
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(stderr_handler)
root.addHandler(stdout_handler)
