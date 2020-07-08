from json import (load as json_load, JSONDecodeError)
from re import (search as re_search, IGNORECASE)
from sys import path
from os.path import sep
from helpers import failure, warning, update_status
from requests import (get as get_request, exceptions)


def waf_detector(url: str) -> dict:
    update_status('Detecting WAF')
    params = {'xss': '<script>alert("XSS")</script>'}  # a payload which is noisy enough to provoke the WAF
    try:
        with open(f'{path[0]}/static/waf_signatures.json') as json_file:
            waf_signatures = json_load(json_file)
        update_status('Getting WAF signatures')
        response = get_request(url, params=params, timeout=10)
        if response.status_code >= 400:
            best_match = dict(score=0, name=None)
            update_status("Iterating over known WAF signatures")
            for name, signature in waf_signatures.items():
                update_status(f"Checking {name}")
                score = 0
                if signature['page'] and re_search(signature['page'], response.text, IGNORECASE):
                    score += 40
                if re_search(signature['code'], str(response.status_code)):
                    score += 20
                if signature['headers'] and re_search(signature['headers'], response.headers.__str__(), IGNORECASE):
                    score += 40
                if score > best_match['score']:
                    best_match['score'] = score
                    best_match['name'] = name
            if best_match['name']:
                return best_match
    except exceptions.RequestException:
        warning("Cannot complete the WAF detection test, you're on your own")
    except (FileNotFoundError, JSONDecodeError):
        failure(f"Error parsing {path[0]}{sep}static{sep}waf_signatures.json ! please review README.md")
