import asyncio

import config
import helpers

try:
    import aiohttp
    from aiohttp import client_exceptions
except ModuleNotFoundError:
    helpers.failure("Missing package: aiohttp")


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
        sem = asyncio.Semaphore(config.maximum_concurrent_connections)
        tasks = []
        simple_trace_config = aiohttp.TraceConfig()
        simple_trace_config.on_request_start.append(self.on_request_start)
        simple_trace_config.on_request_end.append(self.on_request_finish)

        connector = aiohttp.TCPConnector(keepalive_timeout=self.timeout.total, ssl=False)
        async with aiohttp.ClientSession(connector=connector, timeout=self.timeout,
                                         trace_configs=[simple_trace_config]) as session:
            for url in self.url_list:
                tasks.append(asyncio.ensure_future(self.bound_request(sem=sem, url=url, session=session)))
            await asyncio.gather(*tasks)

    async def bound_request(self, sem, url, session):
        async with sem:
            await self.new_request(url=url, session=session)

    async def new_request(self, url, session):
        try:
            async with session.get(url):
                pass
        except (asyncio.exceptions.TimeoutError, client_exceptions.ServerDisconnectedError,
                client_exceptions.ClientConnectorError):
            pass

    @staticmethod
    async def on_request_start(session, trace_config_ctx, params):
        pass

    @staticmethod
    async def on_request_finish(session, trace_config_ctx, params):
        helpers.request_counter(url=params.url.human_repr())
