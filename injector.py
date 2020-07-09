from asyncio import (
    get_event_loop, ensure_future, BoundedSemaphore, gather
)

from aiohttp import (
    ClientTimeout, TraceConfig, TCPConnector, ClientSession
)

from misc.config_loader import USER_CONFIGS
from misc.helpers import (
    failure, successful_request, failed_request
)


class Injector:

    def __init__(self, url_list: list, headers: dict):
        self.__url_list = url_list
        try:
            self.__proxy = USER_CONFIGS.get('http-proxy')
            self.__timeout = ClientTimeout(total=USER_CONFIGS.get('request-timeout'))
            self.__max_con = USER_CONFIGS.get('maximum-concurrent-connections')
            self.__headers = headers
        except Exception as e:
            failure(f"Check config.py \n{e.__str__()}")

        loop = get_event_loop()
        future = ensure_future(self.__run())
        loop.run_until_complete(future)

    async def __run(self):
        sem = BoundedSemaphore(self.__max_con)
        tasks = []
        simple_trace_config = TraceConfig()
        simple_trace_config.on_request_start.append(self.__on_request_start)
        simple_trace_config.on_request_end.append(self.__on_request_finish)

        connector = TCPConnector(keepalive_timeout=self.__timeout.total, ssl=False)
        async with ClientSession(connector=connector, timeout=self.__timeout,
                                 trace_configs=[simple_trace_config]) as session:
            for url in self.__url_list:
                tasks.append(ensure_future(self.__bound_request(sem=sem, url=url, session=session)))
            await gather(*tasks)

    async def __bound_request(self, sem: BoundedSemaphore, url: str, session: ClientSession):
        async with sem:
            await self.__new_request(url=url, session=session)

    async def __new_request(self, url: str, session: ClientSession):
        try:
            async with session.get(url, proxy=self.__proxy, headers=self.__headers, allow_redirects=False):
                pass
        except Exception as e:
            failed_request(url=url, exception=e.__str__())

    @staticmethod
    async def __on_request_start(session, trace_config_ctx, params):
        pass

    @staticmethod
    async def __on_request_finish(session, trace_config_ctx, params):
        successful_request(url=params.url.relative())
