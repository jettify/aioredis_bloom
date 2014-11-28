import asyncio
import aioredis
from aioredis_bloom import BloomFilter


loop = asyncio.get_event_loop()


@asyncio.coroutine
def go():
    redis = yield from aioredis.create_redis(
        ('localhost', 6379), loop=loop)
    bloom = BloomFilter(redis, 100000, 0.0001)
    yield from bloom.add('python')
    yield from bloom.add('asyncio')
    result = yield from bloom.contains('tornado')
    print(result)

    redis.close()
loop.run_until_complete(go())
