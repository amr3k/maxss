import json
from os.path import sep
from random import choice
from sys import path

from misc.helpers import (validate_urls, failure)

try:
    with open(f"{path[0]}{sep}static{sep}config.json") as config_json:
        USER_CONFIGS = json.load(config_json)
        proxy = USER_CONFIGS.get('http-proxy')
        if proxy:
            assert validate_urls([proxy])
        assert type(USER_CONFIGS.get('request-timeout')) == float
except (FileNotFoundError, json.JSONDecodeError, KeyError, AssertionError):
    failure(f"Error parsing {path[0]}{sep}static{sep}config.json ! please review README.md")


def user_agents() -> list:
    try:
        with open(f'{path[0]}{sep}static{sep}user-agents.json') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        failure("Couldn't load user-agents.json file")


def load_payloads() -> list:
    try:
        with open(f"{path[0]}{sep}static{sep}payloads.txt") as payloads_file:
            raw_payload_list = list(filter(None, set(map(str.strip, payloads_file.readlines()))))
        payload_list = raw_payload_list.copy()
        for p in raw_payload_list:
            if p.startswith('#'):
                payload_list.remove(p)
        if len(payload_list) == 0:
            failure('Looks like you forgot to add your own xss payload! check static{sep}payloads.txt')
        return payload_list
    except (FileNotFoundError, BufferError, IOError, OSError, UnicodeError):
        failure("Error while parsing static{sep}payloads.txt")


def headers() -> list:
    headers_list = []
    for p in load_payloads():
        headers_list.append({
            'User-Agent': f"{choice(user_agents())}{p}",
            'Referral': p
        })
    return headers_list
