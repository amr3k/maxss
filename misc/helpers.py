from datetime import datetime
from json import load as json_load, JSONDecodeError
from logging import (
    info as log_info,
    warning as log_warning,
    critical as log_critical,
    error as log_error,
    basicConfig as log_basicConfig,
    INFO as LOG_INFO
)
from os import mkdir
from os.path import sep
from re import match, sub
from sys import exit, path
from time import time, sleep

from halo import Halo

live_status = Halo(spinner='dots12')
live_status.start()

CURRENT_TIME = datetime.fromtimestamp(time()).strftime("%Y%m%d%H%M")
CURRENT_DIR = path[0]
SCRAPPED_DATA_DIR = f'{CURRENT_DIR}{sep}dump{sep}scrapped_data'
LOG_FILE_PATH = ""
URL_COUNT = 0
SENT_REQUESTS = 0
HEADER_COUNT = 0

SUCCESSFUL_ATTEMPTS = 0
FAILED_ATTEMPTS = 0


def color(color: str):
    live_status.text_color = color


def update_status(message: str):
    color('white')
    live_status.text = message
    log_info(message)


def warning(message: str, error: str = None):
    color('yellow')
    live_status.text = f"⚠ {message}"
    log_warning(f"{message} ... {error}")


def critical(message: str):
    live_status.text = f"⛔ {message}"
    log_critical(f"{message}")


def final_stats():
    live_status.info(f"Total URLS: {URL_COUNT}")
    log_info(f"Total URLS: {URL_COUNT}")
    live_status.info(f"Successful attempts: {SUCCESSFUL_ATTEMPTS}")
    log_info(f"Successful attempts: {SUCCESSFUL_ATTEMPTS}")
    live_status.info(f"Failed attempts: {FAILED_ATTEMPTS}")
    log_info(f"Failed attempts: {FAILED_ATTEMPTS}")
    try:
        success_rate = f"{(SUCCESSFUL_ATTEMPTS / (URL_COUNT * HEADER_COUNT)):.0%}"
    except ZeroDivisionError:
        success_rate = "0%"
    live_status.info(f"Success rate = {success_rate}")
    log_info(f"Success rate = {success_rate}")
    live_status.info(f"Full log file: {LOG_FILE_PATH}")


def success(message: str):
    color('green')
    live_status.succeed(text=message)
    final_stats()
    log_info(message)


def failure(message: str):
    color('red')
    final_stats()
    live_status.fail(text=message)
    log_error(message)
    exit(1)


def increase_sent_request_by_1():
    """
    I saved extra two lines using this function
    :return:
    """
    global SENT_REQUESTS
    SENT_REQUESTS += 1


def failed_request(url: str, exception: str = None):
    global FAILED_ATTEMPTS

    increase_sent_request_by_1()
    color('red')
    live_status.text = f"({SENT_REQUESTS}/{URL_COUNT}) Could not reach {url}"
    FAILED_ATTEMPTS += 1
    log_warning(f"Could not reach {url} {exception}")


def successful_request(url: str):
    global SUCCESSFUL_ATTEMPTS

    increase_sent_request_by_1()
    color('blue')
    live_status.text = f"({SENT_REQUESTS}/{URL_COUNT}) Sending to {url}"
    SUCCESSFUL_ATTEMPTS += 1
    log_info(f"Sending to {url}")


def create_log_file(domain):
    global LOG_FILE_PATH
    try:
        create_output_dirs()
        LOG_FILE_PATH = f"{CURRENT_DIR}{sep}dump{sep}logs{sep}{domain}_{CURRENT_TIME}.log"
        log_basicConfig(format="%(asctime)s (%(process)d) [%(filename)s:%(lineno)3d] [%(levelname)s]: %(message)s",
                        level=LOG_INFO,
                        filename=LOG_FILE_PATH,
                        filemode="w", datefmt="[%Y-%m-%d %H:%M]")
    except (OSError, IOError, BufferError, PermissionError, WindowsError):
        failure("Cannot create log file, check your submitted file name")


def create_output_dirs():
    try:
        global SCRAPPED_DATA_DIR
        mkdir(f"{CURRENT_DIR}{sep}dump")
        mkdir(SCRAPPED_DATA_DIR)
        mkdir(f"{CURRENT_DIR}{sep}dump{sep}logs")
    except FileExistsError:
        pass


def extension_list() -> list:
    try:
        with open(f"{CURRENT_DIR}{sep}static{sep}extensions.json") as file:
            return list(json_load(file))
    except (FileNotFoundError, JSONDecodeError):
        failure(f"The file {CURRENT_DIR}/static/extensions.json is either corrupted or not found ")


def check_target_domain(target_domain):
    update_status("Validating domain")
    try:
        if not match('^([a-z0-9\-_]+\.)+[a-z]{2,6}$', target_domain):
            failure("Invalid domain! Please type a valid domain name like google.com or mail.google.com")
    except TypeError:
        failure("Invalid domain")


def validate_urls(url_list: list) -> list:
    update_status("Validating URL list")
    final_list = []
    try:
        for u in url_list:
            if not u.startswith('http'):
                u = f'http://{u}'
            if match('^https?://[a-zA-Z0-9@:_]{2,256}\.[a-z]{2,6}[-a-zA-Z0-9@:%_+.~#?&/=]*$', u):
                final_list.append(sub(':[0-9]{2,5}', '', u))
    except (TypeError, UnicodeError):
        failure('Failed while examining URL list')
    return sanitize_urls(final_list)


def sanitize_urls(url_list: list) -> list:
    update_status("Removing unnecessary links")
    final_urls = url_list.copy()
    for url in url_list:
        url = url.strip()
        for extension in extension_list():
            if url.find(f'.{extension}?') > 0 or url.endswith(f'.{extension}'):
                final_urls.remove(url)
    return list(filter(None, final_urls))  # To remove empty lines


def check_waf_status(domain: str):
    from misc.waf_detector import waf_detector
    result = waf_detector(f"http://{domain}")
    if result[0]:
        critical(result[1])
        for i in reversed(range(1, 6)):
            live_status.text = f"{result[1]} ... Resuming in {i}"
            sleep(1)
    else:
        warning(result[1])
