import sys

try:
    import helpers
    import config
    from fetch_and_filter import FetchAndFilter
    from inject_xss import InjectXSS
    import click
except ModuleNotFoundError:
    sys.exit("Please install missing packages with pip install -r requirements.txt")

helpers.init_halo()


def distribute(url_list: list):
    for i in range(0, len(url_list), config.maximum_concurrent_connections):
        injector = InjectXSS(url_list=url_list[i:i + config.maximum_concurrent_connections])


@click.command()
@click.version_option(version='1.0.0')
@click.option('--domain', '-d', help="Target domain")
@click.option('--archive', '-a', default=True,
              help="Whether you like to fetch a list of URLs from archive.org")
@click.option('--file', '-f', default=False,
              help="If you have a file containing list of URLs, you can provide it here and skip searching Archive.org")
def start(domain, archive=False, file=None):
    helpers.create_log_file(domain)
    helpers.check_target_domain(domain)
    try:
        if archive == True:
            get_urls = FetchAndFilter(target_domain=domain)
            with open(get_urls.file_path) as file:
                url_list = list(set(map(str.strip, file.readlines())))
        elif file:
            with open(file) as raw_file:
                url_list = list(set(map(str.strip, raw_file.readlines())))
        else:
            helpers.failure('Please either choose --archive or provide your own file')
        helpers.URL_COUNT = len(url_list)
        distribute(url_list=url_list)
        helpers.success("All Done!")
    except KeyboardInterrupt:
        helpers.failure("Interrupted by user")


if __name__ == '__main__':
    start()
