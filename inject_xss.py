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
            failure(f"Check config.py \n{e.__str__()}")

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
                request_counter(url)
                return response
        except Exception as e:
            failure(e.__str__())

    async def on_request_start(self, session, trace_config_ctx, params):
        pass

    async def on_request_finish(self, session, trace_config_ctx, params):
        request_counter(params.url)


if __name__ == '__main__':
    import asyncio
    import config
    from fetch_and_filter import FetchAndFilter
    from helpers import *

    try:
        import aiohttp
    except ModuleNotFoundError:
        failure("Missing package: aiohttp")
    try:
        sys.argv.append("video.techcrunch.com")  # TODO delete this line
        target_domain = sys.argv[1]
        check_target_domain(target_domain)
        create_log_file(target_domain)
    except IndexError:
        usage_msg()
    try:
        get_urls = FetchAndFilter(target_domain=target_domain)
        with open(get_urls.file_path) as file:
            url_list = list(set(map(str.strip, file.readlines())))
        injector = InjectXSS(url_list=url_list)
        # distribute(get_urls.file_path)
        success("All Done!")
    except KeyboardInterrupt:
        failure("Interrupted by user")
