import sys
from random import choice
import json
import helpers

proxy = ""
maximum_concurrent_connections = 10
timeout = 3  # Timeout for each request (n seconds)
xss_hunter_payload = ''
try:
    with open(f'{sys.path[0]}/user-agents.json') as file:
        user_agents = json.load(file)
except Exception:
    helpers.failure("Couldn't load user-agents.json file")
headers = {
    'User-Agent': f"{choice(user_agents)}{xss_hunter_payload}"
}

if __name__ == '__main__':
    print(headers)
