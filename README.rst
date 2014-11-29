aioredis_bloom
==============

.. image:: https://travis-ci.org/jettify/aioredis_bloom.svg
    :target: https://travis-ci.org/jettify/aioredis_bloom
    :alt: |Build status|

A simple bloom filter written in Python 3 with asyncio_ using, redis
( aioredis_ ) as storage and the Murmur (mmh3_) hash.


Simple example api:
-------------------
.. code:: python

    import asyncio
    import aioredis
    from aioredis_bloom import BloomFilter


    loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def go():
        redis = yield from aioredis.create_redis(
            ('localhost', 6379), loop=loop)
        capacity = 100000  # expected capacity of bloom filter
        error_rate = 0.0001  # expected error rate
        # size of underlying array is calculated from capacity and error_rate
        bloom = BloomFilter(redis, 100000, 0.0001)
        yield from bloom.add('python')
        yield from bloom.add('asyncio')
        result = yield from bloom.contains('tornado')
        assert result==False

        redis.close()
    loop.run_until_complete(go())

Intersection and union of two bloom filters:
--------------------------------------------
.. code:: python

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

        # init data in both bloom filters
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


Requirements
------------

* Python_ 3.3+
* asyncio_ or Python_ 3.4+
* aioredis_
* mmh3_


TODO
----
1) add support for aioredis pool
2) refactor doc string
3) add alternative constructor using size and num of hash functions


Thanks
------
I've learned a lot from following projects:

* https://github.com/jaybaird/python-bloomfilter
* https://github.com/dariajung/bloom
* https://github.com/bkz/bloom
* https://github.com/acruise/cassandra-bloom-filter


License
-------

The *aioredis_bloom* is offered under MIT license.

.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _aioredis: https://github.com/aio-libs/aioredis
.. _mmh3: https://pypi.python.org/pypi/mmh3/
