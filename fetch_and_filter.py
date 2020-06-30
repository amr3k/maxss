class FetchAndFilter:
    TARGET_DOMAIN = ""
    BASE_URL = "https://web.archive.org/cdx/search/cdx?url=*.{domain}&output=text&fl=original&collapse=urlkey"
    RAW_URLS = ""
    FINAL_URLS = []
    STATIC_FILES = []

    def __init__(self, target_domain: str = None):
        """
        Search Archive.org for all links that includes provided domain name
        and apply sanitizing filter to those links, then export to a text file.
        :param target_domain: [Optional]
        """
        self.check_target_domain(target_domain)
        self.load_extensions()
        self.fetch_url_list()
        self.sanitize_urls()
        self.create_output_dir()
        self.export_data()

    def check_target_domain(self, target_domain=None):
        if target_domain:
            self.TARGET_DOMAIN = target_domain
            return
        try:
            self.TARGET_DOMAIN = sys.argv[1]
        except IndexError:
            helpers.error(f"Usage: {sys.argv[0]} target_domain")
        if not re.match('^[a-z]+([a-z]+.)+[a-z]+$', self.TARGET_DOMAIN):
            helpers.error("Please type only the target domain like google.com or sub-domain like mail.google.com")

    def load_extensions(self):
        try:
            with open("static_file_extensions.json") as file:
                self.STATIC_FILES = json.loads(file.read())  # Add more as you like
        except FileNotFoundError:
            helpers.error("Couldn't find static_file_extensions.json")
        except Exception:
            helpers.error("static_file_extensions.json file is corrupted")

    def fetch_url_list(self):
        """
        Fetch archived links from archive.org
        :return:
        """
        try:
            response = requests.get(self.BASE_URL.format(domain=self.TARGET_DOMAIN))
            assert response.status_code == 200
            assert len(response.text) > len(self.TARGET_DOMAIN)
            self.RAW_URLS = response.text
            self.RAW_URLS = list(set(map(str.strip, self.RAW_URLS.split('\n'))))
            self.FINAL_URLS = self.RAW_URLS.copy()
        except requests.exceptions.RequestException:
            helpers.error("Couldn't connect to archive.org")
        except AssertionError:
            helpers.error(f"Nothing found about {self.TARGET_DOMAIN}")

    def sanitize_urls(self):
        """
        Remove unnecessary links like css, jpg files
        :return:
        """
        for url in self.RAW_URLS:
            for extension in self.STATIC_FILES:
                if url.find(f'.{extension}?') > 0 or url.endswith(f'.{extension}'):
                    self.FINAL_URLS.remove(url)
        self.FINAL_URLS = list(filter(None, self.FINAL_URLS))  # To remove empty strings

    def create_output_dir(self):
        try:
            os.mkdir('output')
        except FileExistsError:
            pass

    def export_data(self):
        try:
            with open(f'output/{self.TARGET_DOMAIN}.txt', 'w') as output_file:
                output_file.write('\n'.join(self.FINAL_URLS))
        except (FileNotFoundError, PermissionError, IOError) as e:
            helpers.error(f"Couldn't write results to the target directory output/{self.TARGET_DOMAIN}\n{e}")


if __name__ == '__main__':
    import re
    import sys
    import os
    import json
    import requests
    import helpers

    test_url = FetchAndFilter()
