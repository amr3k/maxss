import sys
from os.path import sep

try:
    import helpers
    import config_loader
    import web_archive
    import injector
    import click
except ModuleNotFoundError:
    sys.exit("Please install missing packages with pip install -r requirements.txt")


def distribute(url_list: list):
    final_list = helpers.validate_urls(url_list)
    helpers.URL_COUNT = len(final_list)
    helpers.update_status(f"Validating URLS is done, now I have {helpers.URL_COUNT} to work with")
    mcc = config_loader.USER_CONFIGS.get('maximum-concurrent-connections')
    helpers.update_status("Getting headers")
    for h in config_loader.headers():
        helpers.update_status(f"Trying payload: ({h.get('Referral')})")
        for i in range(0, helpers.URL_COUNT, mcc):
            injector.Injector(url_list=final_list[i:i + mcc], headers=h)


@click.command()
@click.version_option(version='1.0.0')
@click.option('--domain', '-d', help="Target domain")
@click.option('--archive', '-a', default=False, show_default=True, is_flag=True,
              help="Fetch latest update from archive.org (skipping existing cached file)")
@click.option('--file', '-f',
              help="If you have a file containing list of URLs, you can provide it here and skip searching Archive.org")
def start(domain, archive=False, file=None):
    try:
        assert sys.version_info >= (3, 7)
        if file:
            try:
                helpers.create_log_file(file[file.rfind(sep) + 1:])
                with open(file) as raw_file:
                    url_list = list(set(map(str.strip, raw_file.readlines())))
            except (IsADirectoryError, FileNotFoundError, PermissionError, BufferError):
                helpers.failure(f"Could not open {file}")
        else:
            helpers.create_log_file(domain)
            helpers.check_target_domain(domain)
            get_urls = web_archive.WebArchive(target_domain=domain, force_fetch=archive)
            with open(get_urls.file_path) as file:
                url_list = list(set(map(str.strip, file.readlines())))
        distribute(url_list=url_list)
        helpers.success("All Done!")
    except AssertionError:
        sys.exit("Sorry, you need at least Python 3.7 to run this script")
    except KeyboardInterrupt:
        helpers.failure("Interrupted by user")


if __name__ == '__main__':
    start()
