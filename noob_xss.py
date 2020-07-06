import sys

try:
    import helpers
    import config
    from web_archive import WebArchive
    from injector import Injector
    import click
except ModuleNotFoundError:
    sys.exit("Please install missing packages with pip install -r requirements.txt")


def distribute(url_list: list):
    final_list = helpers.validate_urls(url_list)
    helpers.URL_COUNT = len(final_list)
    helpers.update_status(f"Validating URLS is done, now I have {helpers.URL_COUNT} to work with")

    for i in range(0, helpers.URL_COUNT, config.maximum_concurrent_connections):
        injector = Injector(url_list=final_list[i:i + config.maximum_concurrent_connections])


@click.command()
@click.version_option(version='1.0.0')
@click.option('--domain', '-d', required=True, help="Target domain")
@click.option('--archive', '-a', default=False, show_default=True, is_flag=True,
              help="Fetch latest update from archive.org (skipping existing cached file)")
@click.option('--file', '-f',
              help="If you have a file containing list of URLs, you can provide it here and skip searching Archive.org")
def start(domain, archive=False, file=None):
    try:
        helpers.create_log_file(domain)
        helpers.check_target_domain(domain)
        if file:
            with open(file) as raw_file:
                url_list = list(set(map(str.strip, raw_file.readlines())))
        else:
            if archive:
                get_urls = WebArchive(target_domain=domain, force_fetch=True)
            else:
                get_urls = WebArchive(target_domain=domain)
            with open(get_urls.file_path) as file:
                url_list = list(set(map(str.strip, file.readlines())))
        distribute(url_list=url_list)
        helpers.success("All Done!")
    except KeyboardInterrupt:
        helpers.failure("Interrupted by user")


if __name__ == '__main__':
    start()
