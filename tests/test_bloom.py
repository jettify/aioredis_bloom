import aioredis
from aioredis_bloom.bloom import BloomFilter

from ._testutil import BaseTest, run_until_complete


class ConnectionTest(BaseTest):

    @run_until_complete
    def test_redis_connection(self):
        redis = yield from aioredis.create_redis(
            ('localhost', 6379), loop=self.loop)
        yield from redis.set('my-key', 'value')
        val = yield from redis.get('my-key')
        self.assertEqual(b'value', val)

    @run_until_complete
    def test_instance_creation(self):
        redis = yield from aioredis.create_redis(
            ('localhost', 6379), loop=self.loop)
        bloom = BloomFilter(redis, 'bloom', 100000, 0.0001)
        assert bloom._conn
