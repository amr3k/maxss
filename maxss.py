from multiprocessing import Process, cpu_count
from os.path import sep
from sys import exit, version_info

try:
    import helpers
    import config_loader
    import web_archive
    import injector
    import click
except ModuleNotFoundError:
    exit("Please install missing packages with pip install -r requirements.txt")


def distribute(url_list: list):
    injector.Injector(url_list=final_list, headers=config_loader.headers()[0])
    for h in config_loader.headers():
        helpers.update_status(f"Trying payload: ({h.get('Referral')})")
        injector.Injector(url_list=final_list, headers=h)
        cores = cpu_count()
        if cores == 1:
            p = Process(target=injector.Injector, args=(final_list, h,))
            p.start()
            p.join()
        else:
            process_list = []
            for i in range(cores):
                chunk_list = final_list[i * helpers.URL_COUNT // cores:(i + 1) * helpers.URL_COUNT // cores]
                process_list.append(
                    Process(target=injector.Injector, args=(chunk_list, h,)))
            for p in process_list:
                p.start()
            for p in process_list:
                p.join()


@click.command()
@click.version_option(version='1.0.0')
@click.option('--domain', '-d', help="Target domain")
@click.option('--archive', '-a', default=False, show_default=True, is_flag=True,
              help="Fetch latest update from archive.org (skipping existing cached file)")
@click.option('--file', '-f',
              help="If you have a file containing list of URLs, you can provide it here and skip searching Archive.org")
def start(domain, archive=False, file=None):
    try:
        assert version_info >= (3, 7)
        if file:
            try:
                helpers.create_log_file(file[file.rfind(sep) + 1:])
                with open(file) as raw_file:
                    raw_list = list(set(map(str.strip, raw_file.readlines())))
                url_list = helpers.validate_urls(raw_list)
            except (IsADirectoryError, FileNotFoundError, PermissionError, BufferError):
                helpers.failure(f"Could not open {file}")
        else:
            helpers.create_log_file(domain)
            helpers.check_target_domain(domain)
            get_urls = web_archive.WebArchive(target_domain=domain, force_fetch=archive)
            url_list = get_urls.FINAL_URLS

        helpers.URL_COUNT = len(url_list)
        helpers.update_status(f"Now I have {helpers.URL_COUNT} to work with")

        distribute(url_list=url_list)
        helpers.success("All Done!")
    except AssertionError:
        exit("Sorry, you need at least Python 3.7 to run this script")
    except KeyboardInterrupt:
        helpers.failure("Interrupted by user")


if __name__ == '__main__':
    start()
