import asyncio
import aioredis
from aioredis_bloom import BloomFilter


loop = asyncio.get_event_loop()


@asyncio.coroutine
def go():
    redis = yield from aioredis.create_redis(
        ('localhost', 6379), loop=loop)

    bloom1 = BloomFilter(redis, 1000, 0.001, 'bloom:1')
    bloom2 = BloomFilter(redis, 1000, 0.001, 'bloom:2')

    yield from bloom1.add('tornado')
    yield from bloom1.add('python')

    yield from bloom2.add('asyncio')
    yield from bloom2.add('python')

    # intersection
    inter_bloom = yield from bloom1.intersection(bloom2)

    in_bloom1 = yield from inter_bloom.contains('python')
    print(in_bloom1)  # True
    in_bloom2 = yield from inter_bloom.contains('asyncio')
    print(in_bloom2)  # False

    # union
    union_bloom = yield from bloom1.intersection(bloom2)

    in_bloom1 = yield from union_bloom.contains('python')
    print(in_bloom1)  # True
    in_bloom2 = yield from union_bloom.contains('asyncio')
    print(in_bloom2)  # True

    redis.close()

loop.run_until_complete(go())
