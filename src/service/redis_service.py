import redis

class RedisService:
    _client = None

    @classmethod
    def configure(cls, host='localhost', port=6379, db=0):
        cls._client = redis.Redis(host=host, port=port, db=db)

    @classmethod
    def set(cls, key, value):
        if cls._client is None:
            cls.configure()
        cls._client.set(key, value)

    @classmethod
    def get(cls, key):
        if cls._client is None:
            cls.configure()
        value = cls._client.get(key)
        if value:
            return value.decode()
        return None
