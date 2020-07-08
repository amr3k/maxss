from json import loads, JSONDecodeError
from os.path import sep, isfile
from sys import path

from requests import get as get_request
from requests.exceptions import RequestException

import helpers


class WebArchive:
    FINAL_URLS = []

    def __init__(self, target_domain: str, force_fetch=False):
        """
        Search Archive.org for all links that includes provided domain name
        and apply sanitizing filter to those links, then export to a text file.
        :param target_domain: String
        :param force_fetch: Bool
        """
        self.TARGET_DOMAIN = target_domain
        self.__file_path = f"{path[0]}{sep}output{sep}{self.TARGET_DOMAIN}.txt"
        if self.__cached_file() and not force_fetch:
            helpers.update_status(f"Found cached file at ({self.__file_path}), skipping archive.org")
            return
        helpers.create_output_dir()
        helpers.update_status('Starting requester')
        self.FINAL_URLS = self.__fetch_url_list()
        self.__export_data()

    def __fetch_url_list(self) -> list:
        """
        Fetch cached links from archive.org
        :return: list
        """
        try:
            helpers.update_status('Getting list of URLs')
            response = get_request(
                url=f'https://web.archive.org/cdx/search/cdx?url={self.TARGET_DOMAIN}&matchType=prefix&output=json&fl'
                    f'=original&filter=!statuscode:404&collapse=urlkey')
            helpers.update_status('Connected to Archive.org')
            dump = [u[0] for u in loads(response.text)]
            dump.pop(0)
            assert len(dump) > 0
            helpers.update_status("Fetched data from archive.org")
            return helpers.validate_urls(dump)
        except RequestException:
            helpers.failure("Couldn't connect to archive.org")
        except (AssertionError, JSONDecodeError, IndexError):
            helpers.failure(f"Nothing found about {self.TARGET_DOMAIN}")

    def __export_data(self):
        try:
            with open(self.__file_path, 'w') as output_file:
                output_file.write('\n'.join(self.FINAL_URLS))
        except (FileNotFoundError, PermissionError, IOError) as e:
            helpers.failure(
                f"Could not write results to the target directory output{sep}{self.TARGET_DOMAIN}\n{e}")

    def __cached_file(self):
        return isfile(self.__file_path)
