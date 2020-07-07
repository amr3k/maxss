import json
import sys
from random import choice

import helpers

try:
    with open(f"{sys.path[0]}/static/config.json") as config_json:
        settings = json.load(config_json)

        USER_CONFIGS = {
            "http-proxy": settings['http-proxy'],
            "maximum_concurrent_connections": settings['maximum-concurrent-connections'],
            "request-timeout": settings['request-timeout'],  # Timeout for each request (n seconds)
        }
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    helpers.failure("Error parsing config.json file")


def user_agents() -> list:
    try:
        with open(f'{sys.path[0]}/static/user-agents.json') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        helpers.failure("Couldn't load user-agents.json file")


def load_payloads() -> list:
    try:
        with open(f"{sys.path[0]}/static/payloads.txt") as payloads_file:
            raw_payload_list = list(filter(None, set(map(str.strip, payloads_file.readlines()))))
        payload_list = raw_payload_list.copy()
        for p in raw_payload_list:
            if p.startswith('#'):
                payload_list.remove(p)
        if len(payload_list) == 0:
            helpers.failure('Looks like you forgot to add your own xss payload! check static/payloads.txt')
        return payload_list
    except (FileNotFoundError, BufferError, IOError, OSError, UnicodeError):
        helpers.failure("Error while parsing static/payloads.txt")


def headers() -> list:
    headers_list = []
    for p in load_payloads():
        headers_list.append({
            'User-Agent': f"{choice(user_agents())}{p}",
            'Referral': p
        })
    return headers_list


if __name__ == '__main__':
    print(load_payloads())
