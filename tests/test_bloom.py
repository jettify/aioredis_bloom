import asyncio
from aioredis import create_redis
from aioredis_bloom.bloom import BloomFilter

from ._testutil import BaseTest, run_until_complete


class BloomFilterTest(BaseTest):


    def setUp(self):
        super().setUp()
        self.redis = self.loop.run_until_complete(create_redis(
        ('localhost', 6379), loop=self.loop))
        self.loop.run_until_complete(self._delete_test_keys())

    def tearDown(self):

        self.redis.close()
        del self.redis
        super().tearDown()

    @asyncio.coroutine
    def _delete_test_keys(self):
        keys = yield from self.redis.keys('*test_bloom*')
        if keys:
            yield from self.redis.delete(*keys)

    @run_until_complete
    def test_instance_creation(self):

        redis_key = 'test_bloom:instance'
        capacity = 100000
        error_rate = 0.001

        bloom = BloomFilter(self.redis, capacity, error_rate, redis_key)
        self.assertEqual(bloom.redis_key, redis_key)
        self.assertEqual(bloom.capacity, capacity)
        self.assertEqual(bloom.error_rate, error_rate)

    @run_until_complete
    def test_add_contains(self):

        bloom = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:add')
        yield from bloom.add('key')
        in_bloom = yield from bloom.contains('key')

        self.assertTrue(in_bloom)

        for i in range(100):
            yield from bloom.add('key:{}'.format(i))

        for i in range(100):
            in_bloom = yield from bloom.contains('key:{}'.format(i))
            self.assertTrue(in_bloom)

        for i in range(100):
            in_bloom = yield from bloom.contains('not:key:{}'.format(i))
            self.assertFalse(in_bloom)

    @run_until_complete
    def test_union(self):
        bloom1 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:1')
        bloom2 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:2')
        bloom3 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:3')

        # two blooms have no same values
        yield from bloom3.add('unique_value')
        bloom_with_u = yield from bloom1.union(bloom3, 'test_bloom:with_u')
        in_bloom = yield from bloom_with_u.contains('unique_value')
        self.assertTrue(in_bloom)

        # two blooms have same values
        for i in range(100):
            yield from bloom1.add('bloom:1:{}'.format(i))
            yield from bloom2.add('bloom:2:{}'.format(i))

        new_bloom = yield from bloom1.union(bloom2, )

        for i in range(100):
            in_bloom1 = yield from new_bloom.contains('bloom:1:{}'.format(i))
            in_bloom2 = yield from new_bloom.contains('bloom:2:{}'.format(i))
            not_in_bloom = yield from new_bloom.contains('xxx:2:{}'.format(i))
            self.assertTrue(in_bloom1)
            self.assertTrue(in_bloom2)
            self.assertFalse(not_in_bloom)

    @run_until_complete
    def test_intersection_empty_set(self):
        bloom1 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:1')
        bloom2 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:2')

        for i in range(100):
            yield from bloom1.add('bloom:1:{}'.format(i))
            yield from bloom2.add('bloom:2:{}'.format(i))

        new_bloom = yield from bloom1.intersection(bloom2, 'inter:test_bloom')

        # intersection is empty set
        for i in range(100):
            in_bloom1 = yield from new_bloom.contains('bloom:1:{}'.format(i))
            in_bloom2 = yield from new_bloom.contains('bloom:2:{}'.format(i))
            self.assertFalse(in_bloom1)
            self.assertFalse(in_bloom2)

    @run_until_complete
    def test_intersection(self):
        bloom1 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:1')
        bloom2 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:2')



        for i in range(100):
            # common elements in both filters
            yield from bloom1.add('bloom:x:{}'.format(i))
            yield from bloom2.add('bloom:x:{}'.format(i))
            # unique element ins both filters
            yield from bloom2.add('bloom:1:{}'.format(i))
            yield from bloom2.add('bloom:2:{}'.format(i))

        new_bloom = yield from bloom1.intersection(bloom2)

        # intersection is empty set
        for i in range(100):
            # must be in bloom
            in_bloomx = yield from new_bloom.contains('bloom:x:{}'.format(i))
            self.assertTrue(in_bloomx)
            # must not be in bloom
            in_bloom1 = yield from new_bloom.contains('bloom:1:{}'.format(i))
            in_bloom2 = yield from new_bloom.contains('bloom:2:{}'.format(i))
            self.assertFalse(in_bloom1)
            self.assertFalse(in_bloom2)

    @run_until_complete
    def test_bloom_validation(self):
        bloom1 = BloomFilter(self.redis, 100000, 0.001, 'test_bloom:union1')
        bloom2 = BloomFilter(self.redis, 100000, 0.1, 'test_bloom:union2')
        bloom3 = BloomFilter(self.redis, 10, 0.001, 'test_bloom:union3')
        # filter capacity not the same
        with self.assertRaises(ValueError):
            yield from bloom1.intersection(bloom2)
        # error rate not the same
        with self.assertRaises(ValueError):
            yield from bloom1.union(bloom3)
        # wrong not instance of BloomFilter
        with self.assertRaises(TypeError):
            yield from bloom1.intersection(['bloom'])
