import asyncio
import os
import unittest

from functools import wraps


def run_until_complete(fun):
    if not asyncio.iscoroutinefunction(fun):
        fun = asyncio.coroutine(fun)

    @wraps(fun)
    def wrapper(test, *args, **kw):
        loop = test.loop
        ret = loop.run_until_complete(fun(test, *args, **kw))
        return ret
    return wrapper


class BaseTest(unittest.TestCase):
    """Base test case for unittests.
    """

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.redis_port = int(os.environ.get('REDIS_PORT') or 6379)
        self.redis_host = str(os.environ.get('REDIS_PORT') or 'localhost')

    def tearDown(self):
        self.loop.close()
        del self.loop
