class InjectXSS:
    def __init__(self):
        pass


if __name__ == '__main__':
    import os
    import sys
    import multiprocessing
    import fetch_and_filter
    import config
    import helpers

    try:
        import aiohttp
    except ModuleNotFoundError:
        helpers.error("Please install required modules")
    cores = multiprocessing.cpu_count()
