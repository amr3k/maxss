class InjectXSS:
    def __init__(self):
        pass


def distribute(target_domain: str):
    try:
        with open(f'output/{target_domain}.txt') as file:
            url_list = list(set(map(str.strip, file.readlines())))
    except (IOError, FileNotFoundError):
        logging.error("Output file not found")
    cores = multiprocessing.cpu_count()
    if cores == 1:
        p = multiprocessing.Process(target=InjectXSS, args=(list, 0,))
        p.start()
        p.join()
    else:
        ps = []
        chunk = int(limit / instances)
        for i in range(0, len(list), chunk):
            ps.append(multiprocessing.Process(target=InjectXSS, args=(list[i:i + chunk], int(i / chunk),)))
        for p in ps:
            p.start()
        for p in ps:
            p.join()


if __name__ == '__main__':
    import os
    import sys
    import multiprocessing
    import logging
    import fetch_and_filter
    import config
    import helpers

    try:
        import aiohttp
    except ModuleNotFoundError:
        helpers.failure("Missing package: aiohttp")
    try:
        sys.argv.append("oktob.io")  # TODO delete this line
        target_domain = sys.argv[1]
        helpers.check_target_domain(target_domain)
        helpers.create_log_file(target_domain)
    except IndexError:
        helpers.usage_msg()
    try:
        # distribute(target_domain)
        helpers.success("All Done!")
    except KeyboardInterrupt:
        helpers.failure("Interrupted by user")
