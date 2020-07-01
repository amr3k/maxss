class InjectXSS:
    proxy = {}
    headers = []

    def __init__(self, url_list: list):
        self.url_list = url_list
        try:
            self.proxy = config.proxy
            self.headers = config.headers
            self.timeout = aiohttp.ClientTimeout(total=config.timeout)
        except Exception as e:
            helpers.failure(f"Check config.py \n{e.__str__()}")

        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.run())
        loop.run_until_complete(future)

    async def run(self):
        tasks = []
        simple_trace_config = aiohttp.TraceConfig()
        simple_trace_config.on_request_start.append(self.on_request_start)
        simple_trace_config.on_request_end.append(self.on_request_finish)

        connector = aiohttp.TCPConnector(limit=config.maximum_concurrent_connections, keepalive_timeout=self.timeout)
        async with aiohttp.ClientSession(connector=connector, timeout=self.timeout,
                                         trace_configs=[simple_trace_config]) as session:
            for url in self.url_list:
                tasks.append(asyncio.ensure_future(self.new_request(url=url, session=session)))
            await asyncio.gather(*tasks)

    async def new_request(self, url, session):
        try:
            async with session.get(url) as response:
                helpers.request_counter(url)
                return response
        except Exception as e:
            helpers.failure(e.__str__())

    async def on_request_start(self, session, trace_config_ctx, params):
        pass

    async def on_request_finish(self, session, trace_config_ctx, params):
        helpers.request_counter(params.url)


def distribute(urls_file: str):
    try:
        with open(urls_file) as file:
            url_list = list(set(map(str.strip, file.readlines())))
    except (IOError, FileNotFoundError):
        helpers.failure("Output file not found")
    total_urls = len(url_list)
    helpers.TOTAL_URLS = total_urls
    cores = multiprocessing.cpu_count()
    if cores == 1:
        p = multiprocessing.Process(target=InjectXSS, args=(url_list,))
        p.start()
        p.join()
    else:
        process_list = []
        for i in range(cores):
            chunk_list = url_list[i * total_urls // cores:(i + 1) * total_urls // cores]
            process_list.append(
                multiprocessing.Process(target=InjectXSS, args=(chunk_list,)))
        for p in process_list:
            p.start()
        for p in process_list:
            p.join()


if __name__ == '__main__':
    import os
    import sys
    import multiprocessing
    import asyncio
    import logging
    import fetch_and_filter
    import config
    import helpers

    try:
        import aiohttp
    except ModuleNotFoundError:
        helpers.failure("Missing package: aiohttp")
    try:
        sys.argv.append("video.techcrunch.com")  # TODO delete this line
        target_domain = sys.argv[1]
        helpers.check_target_domain(target_domain)
        helpers.create_log_file(target_domain)
    except IndexError:
        helpers.usage_msg()
    try:
        get_urls = fetch_and_filter.FetchAndFilter()
        distribute(get_urls.file_path)
        helpers.success("All Done!")
    except KeyboardInterrupt:
        helpers.failure("Interrupted by user")
