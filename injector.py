import asyncio

import config_loader
import helpers

try:
    import aiohttp
    from aiohttp import client_exceptions
except ModuleNotFoundError:
    helpers.missing_module()


class Injector:
    __proxy = {}
    __headers = []

    def __init__(self, url_list: list, headers: dict):
        self.__url_list = url_list
        try:
            c = config_loader.USER_CONFIGS
            self.__proxy = c.get('http-proxy')
            self.__timeout = aiohttp.ClientTimeout(total=c.get('request-timeout'))
            self.__headers = headers
        except Exception as e:
            helpers.failure(f"Check config.py \n{e.__str__()}")

        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.__run())
        loop.run_until_complete(future)

    async def __run(self):
        sem = asyncio.BoundedSemaphore(config_loader.USER_CONFIGS.get('maximum_concurrent_connections'))
        tasks = []
        simple_trace_config = aiohttp.TraceConfig()
        simple_trace_config.on_request_start.append(self.__on_request_start)
        simple_trace_config.on_request_end.append(self.__on_request_finish)

        connector = aiohttp.TCPConnector(keepalive_timeout=self.__timeout.total, ssl=False)
        async with aiohttp.ClientSession(connector=connector, timeout=self.__timeout,
                                         trace_configs=[simple_trace_config]) as session:
            for url in self.__url_list:
                tasks.append(asyncio.ensure_future(self.__bound_request(sem=sem, url=url, session=session)))
            await asyncio.gather(*tasks)

    async def __bound_request(self, sem, url, session):
        async with sem:
            await self.__new_request(url=url, session=session)

    @staticmethod
    async def __new_request(url, session):
        try:
            async with session.get(url):
                pass
        except (asyncio.exceptions.TimeoutError, client_exceptions.ServerDisconnectedError,
                client_exceptions.ClientConnectorError, client_exceptions.ClientOSError):
            helpers.failed_request(url=url)

    @staticmethod
    async def __on_request_start(session, trace_config_ctx, params):
        pass

    @staticmethod
    async def __on_request_finish(session, trace_config_ctx, params):
        helpers.successful_request(url=params.url.human_repr())
