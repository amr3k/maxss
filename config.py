import json
import sys
from random import choice

import helpers

try:
    with open(f"{sys.path[0]}/static/config.json") as config_file:
        settings = json.load(config_file)

        proxy = settings['http-__proxy']
        maximum_concurrent_connections = settings['max-connections']
        timeout = settings['__timeout']  # Timeout for each request (n seconds)
        xss_hunter_payload = settings['xss-payload']
except Exception:
    helpers.failure("Error parsing config.json file")
try:
    with open(f'{sys.path[0]}/static/user-agents.json') as file:
        user_agents = json.load(file)
except Exception:
    helpers.failure("Couldn't load user-agents.json file")
headers = {
    'User-Agent': f"{choice(user_agents)}{xss_hunter_payload}"
}

if __name__ == '__main__':
    print(headers)
