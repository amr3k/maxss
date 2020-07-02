import sys
import os
import re
import logging
import json
from datetime import datetime
from time import time


def init_halo():
    try:
        from halo import Halo
    except ModuleNotFoundError:
        sys.exit("Missing package: halo")


init_halo()
from halo import Halo

live_status = Halo()
live_status.start()


def update_status(message: str):
    live_status.text = message
    logging.info(message)


def warning(message: str):
    live_status.warn(message)
    logging.warning(message)


def success(message: str):
    live_status.succeed(text=message)
    logging.info(message)


def failure(message: str):
    live_status.fail(text=message)
    logging.error(message)
    sys.exit(1)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_TIME = datetime.fromtimestamp(time()).strftime("%Y%m%d%H%M")

SENT_REQUESTS = 0


def request_counter(url: str, total_count: int):
    global SENT_REQUESTS

    SENT_REQUESTS += 1
    live_status.text = f"({SENT_REQUESTS} / {total_count}) {url[:120]}"


def create_log_file(domain):
    logging.basicConfig(format="%(asctime)s (%(process)d) [%(filename)s:%(lineno)3d] [%(levelname)s]: %(message)s",
                        level=logging.INFO,
                        filename=f"{CURRENT_DIR}/logs/{domain}_{CURRENT_TIME}.log",
                        filemode="w", datefmt="[%Y-%m-%d %H:%M]")


def usage_msg():
    sys.exit(f"Usage: {sys.argv[0]} target_domain")


def extension_list() -> list:
    try:
        with open(f"{sys.path[0]}/static/extensions.json") as file:
            return json.load(file)  # Add more as you like
    except FileNotFoundError:
        failure("Couldn't find extensions.json")
    except Exception as e:
        failure(f"extensions.json file is corrupted\nFull details:\t{e.__str__()}")


def check_target_domain(target_domain):
    update_status("Checking domain validity")
    if not re.match('^[a-z]+([a-z]+.)+[a-z]+$', target_domain):
        failure("Please type only the target domain like google.com or sub-domain like mail.google.com")
