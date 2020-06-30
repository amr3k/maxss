import re
import sys
import os
import json

try:
    import requests
except ModuleNotFoundError:
    print('Please install requests')
    sys.exit(1)

try:
    TARGET_DOMAIN = sys.argv[1]
except IndexError:
    print("Usage: {} target_domain".format(sys.argv[0]))
    sys.exit(1)

if not re.match('^[a-z]+([a-z]+\.)+[a-z]+$', TARGET_DOMAIN):
    print("Please only the target domain like google.com or subdomain like mail.google.com")
    sys.exit(1)

BASE_URL = "https://web.archive.org/cdx/search/cdx?url=*.{domain}&output=text&fl=original&collapse=urlkey"
RAW_URLS = ""
FINAL_URLS = []
try:
    with open("static_file_extensions.json") as file:
        STATIC_FILES = json.loads(file.read())  # Add more as you like
except FileNotFoundError:
    print("Couldn't find static_file_extensions.json")
    sys.exit(1)
except Exception:
    print("static_file_extensions.json file is corrupted")
    sys.exit(1)

try:
    response = requests.get(BASE_URL.format(domain=TARGET_DOMAIN))
    assert len(response.text) > len(TARGET_DOMAIN)
    RAW_URLS = response.text
except requests.exceptions.RequestException:
    print("Couldn't connect to archive.org")
    sys.exit(1)
except AssertionError:
    print("Nothing found about {}".format(TARGET_DOMAIN))
    sys.exit(1)

RAW_URLS = list(set(map(str.strip, RAW_URLS.split('\n'))))
FINAL_URLS = RAW_URLS.copy()

for url in RAW_URLS:
    for extension in STATIC_FILES:
        if url.find('.{}?'.format(extension)) > 0 or url.endswith('.{}'.format(extension)):
            FINAL_URLS.remove(url)
FINAL_URLS = list(filter(None, FINAL_URLS))  # To remove empty strings
try:
    os.mkdir('output')
except FileExistsError:
    pass

try:
    with open('output/{}.txt'.format(TARGET_DOMAIN), 'w') as output_file:
        output_file.write('\n'.join(FINAL_URLS))
except (FileNotFoundError, PermissionError, IOError) as e:
    print("Couldn't write results to the target directory output/{directory_name}\n{exception}".format(
        directory_name=TARGET_DOMAIN, exception=e))
    sys.exit(1)
