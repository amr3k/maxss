import sys
import os
import re
import logging
from datetime import datetime
from time import time

try:
    from halo import Halo
except ModuleNotFoundError:
    sys.exit("Missing package: halo")
status = Halo()
status.start()


def update_status(message: str):
    status.text = message
    logging.info(message)


def warning(message: str):
    status.warn(message)
    logging.warning(message)


def success(message: str):
    status.succeed(text=message)
    logging.info(message)


def failure(message: str):
    status.fail(text=message)
    logging.error(message)
    sys.exit(1)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_TIME = datetime.fromtimestamp(time()).strftime("%Y%m%d%H%M")


def create_log_file(domain):
    logging.basicConfig(format="%(asctime)s (%(process)d) [%(filename)s:%(lineno)3d] [%(levelname)s]: %(message)s",
                        level=logging.INFO,
                        filename=f"{CURRENT_DIR}/logs/{domain}_{CURRENT_TIME}.log",
                        filemode="w", datefmt="[%Y-%m-%d %H:%M]")


def usage_msg():
    sys.exit(f"Usage: {sys.argv[0]} target_domain")


def check_target_domain(target_domain):
    update_status("Checking domain validity")
    if not re.match('^[a-z]+([a-z]+.)+[a-z]+$', target_domain):
        failure("Please type only the target domain like google.com or sub-domain like mail.google.com")
