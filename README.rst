aioredis_bloom (work in progress)
=================================

A simple bloom filter written in Python 3 with asyncio_ using, redis
(aioreids_) as storage and the Murmur (mmh3_) hash.

Expected api:

.. code:: python

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


Requirements
------------

* Python_ 3.3+
* asyncio_ or Python_ 3.4+
* aioredis_
* mmh3_


License
-------

The *aioredis_bloom* is offered under MIT license.

.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _aioredis: https://github.com/aio-libs/aioredis
.. _mmh3: https://pypi.python.org/pypi/mmh3/
