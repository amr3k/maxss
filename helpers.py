import json
import logging
import re
import sys
from datetime import datetime
from os.path import sep
from time import time

from halo import Halo

CURRENT_DIR = sys.path[0]
CURRENT_TIME = datetime.fromtimestamp(time()).strftime("%Y%m%d%H%M")
LOG_FILE_PATH = ""
URL_COUNT = 0
SENT_REQUESTS = 0

SUCCESSFUL_ATTEMPTS = 0
FAILED_ATTEMPTS = 0

live_status = Halo(spinner='dots12', color='white')
live_status.start()


def update_status(message: str):
    live_status.text_color = 'white'
    live_status.text = message
    logging.info(message)


def warning(message: str):
    live_status.warn(message)
    logging.warning(message)


def final_stats():
    live_status.warn(f"Total URLS: {URL_COUNT}")
    logging.info(f"Total URLS: {URL_COUNT}")
    live_status.warn(f"Successful attempts: {SUCCESSFUL_ATTEMPTS}")
    logging.info(f"Successful attempts: {SUCCESSFUL_ATTEMPTS}")
    live_status.warn(f"Failed attempts: {FAILED_ATTEMPTS}")
    logging.info(f"Failed attempts: {FAILED_ATTEMPTS}")
    try:
        success_rate = f"{(SUCCESSFUL_ATTEMPTS / URL_COUNT):.0%}"
    except ZeroDivisionError:
        success_rate = "0%"
    live_status.warn(f"Success rate = {success_rate}")
    logging.info(f"Success rate = {success_rate}")
    live_status.warn(f"Full log file: {LOG_FILE_PATH}")


def success(message: str):
    live_status.text_color = 'blue'
    live_status.succeed(text=message)
    final_stats()
    logging.info(message)


def failure(message: str):
    live_status.text_color = 'red'
    live_status.fail(text=message)
    logging.error(message)
    final_stats()
    sys.exit(1)


def increase_sent_request_by_1():
    global SENT_REQUESTS
    SENT_REQUESTS += 1


def failed_request(url, exception):
    global FAILED_ATTEMPTS

    increase_sent_request_by_1()
    live_status.text_color = 'red'
    live_status.text = f"({SENT_REQUESTS}/{URL_COUNT}) Could not reach {url}"
    FAILED_ATTEMPTS += 1
    logging.warning(f"Could not reach {url} {exception}")


def successful_request(url: str):
    global SUCCESSFUL_ATTEMPTS

    increase_sent_request_by_1()
    live_status.text_color = 'green'
    live_status.text = f"({SENT_REQUESTS}/{URL_COUNT}) Sending to {url}"
    SUCCESSFUL_ATTEMPTS += 1
    logging.info(f"Sending to {url}")


def create_log_file(domain):
    global LOG_FILE_PATH
    LOG_FILE_PATH = f"{CURRENT_DIR}{sep}logs{sep}{domain}_{CURRENT_TIME}.log"
    logging.basicConfig(format="%(asctime)s (%(process)d) [%(filename)s:%(lineno)3d] [%(levelname)s]: %(message)s",
                        level=logging.INFO,
                        filename=LOG_FILE_PATH,
                        filemode="w", datefmt="[%Y-%m-%d %H:%M]")


def extension_list() -> list:
    try:
        with open(f"{CURRENT_DIR}{sep}static{sep}extensions.json") as file:
            return list(json.load(file))
    except FileNotFoundError:
        failure("Couldn't find extensions.json")
    except Exception as e:
        failure(f"extensions.json file is corrupted\nFull details:\t{e.__str__()}")


def check_target_domain(target_domain):
    update_status("Validating domain")
    try:
        if not re.match('^[a-z]+([a-z]+.)+[a-z]+$', target_domain):
            failure("Invalid domain! Please type a valid domain name like google.com or mail.google.com")
    except TypeError:
        failure("Invalid domain")


def validate_urls(url_list) -> list:
    update_status("Validating URL list")
    final_list = []
    try:
        for u in url_list:
            if not u.startswith('http'):
                u = f'http://{u}'
            if re.match(
                    '^(http(s)?):\/\/[(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9@:%_\+.~#?&//=]*)$',
                    u):
                final_list.append(re.sub(':[0-9]{2,5}', '', u))
    except (TypeError, UnicodeError):
        failure('Failed while examining URL list')
    return sanitize_urls(final_list)


def sanitize_urls(url_list) -> list:
    """
    Remove unnecessary links like css, jpg files
    :return:
    """
    update_status("Removing unnecessary links")
    final_urls = url_list.copy()
    for url in url_list:
        url = url.strip()
        for extension in extension_list():
            if url.find(f'.{extension}?') > 0 or url.endswith(f'.{extension}'):
                final_urls.remove(url)
    return list(filter(None, final_urls))  # To remove empty strings
