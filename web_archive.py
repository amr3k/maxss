import os
import sys

import helpers

try:
    import requests
except ModuleNotFoundError:
    helpers.missing_module()


class WebArchive:
    file_path = ''
    BASE_URL = "https://web.archive.org/cdx/search/cdx?url=*.{domain}&output=text&fl=original&collapse=urlkey"
    RAW_URLS = ""
    FINAL_URLS = []

    def __init__(self, target_domain: str, force_fetch=False):
        """
        Search Archive.org for all links that includes provided domain name
        and apply sanitizing filter to those links, then export to a text file.
        :param target_domain: [Optional]
        """
        self.TARGET_DOMAIN = target_domain
        ds = os.path.sep
        self.file_path = f"{sys.path[0]}{ds}output{ds}{self.TARGET_DOMAIN}.txt"
        if self.cached_file() and not force_fetch:
            helpers.update_status(f"Found cached file at ({self.file_path}), skipping archive.org")
            return
        helpers.update_status('Starting requester')
        self.fetch_url_list()
        self.FINAL_URLS = helpers.validate_urls(self.RAW_URLS)
        self.create_output_dir()
        self.export_data()

    def fetch_url_list(self):
        """
        Fetch archived links from archive.org
        :return:
        """
        try:
            helpers.update_status('Getting list of URLs')
            response = requests.get(self.BASE_URL.format(domain=self.TARGET_DOMAIN))
            assert response.status_code == 200
            helpers.update_status('Connected to Archive.org')
            assert len(response.text) > len(self.TARGET_DOMAIN)
            self.RAW_URLS = response.text
            self.RAW_URLS = list(set(map(str.strip, self.RAW_URLS.split('\n'))))
            self.FINAL_URLS = self.RAW_URLS.copy()
        except requests.exceptions.RequestException:
            helpers.failure("Couldn't connect to archive.org")
        except AssertionError:
            helpers.failure(f"Nothing found about {self.TARGET_DOMAIN}")

    @staticmethod
    def create_output_dir():
        try:
            os.mkdir('output')
        except FileExistsError:
            pass

    def export_data(self):
        try:
            with open(self.file_path, 'w') as output_file:
                output_file.write('\n'.join(self.FINAL_URLS))
        except (FileNotFoundError, PermissionError, IOError) as e:
            helpers.failure(
                f"Could not write results to the target directory output{os.path.sep}{self.TARGET_DOMAIN}\n{e}")

    def cached_file(self):
        return os.path.isfile(self.file_path)
