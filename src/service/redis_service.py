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
    
    # -------- HASH METHODS --------

    @classmethod
    def hset(cls, key, field, value):
        """Set field in hash key."""
        if cls._client is None:
            cls.configure()
        return cls._client.hset(key, field, value)

    @classmethod
    def hget(cls, key, field):
        """Get value of field in hash key."""
        if cls._client is None:
            cls.configure()
        value = cls._client.hget(key, field)
        if value:
            return value.decode()
        return None

    @classmethod
    def hgetall(cls, key):
        """Get all fields and values in hash key as dict of strings."""
        if cls._client is None:
            cls.configure()
        data = cls._client.hgetall(key)
        # data is dict bytes->bytes, decode to str->str
        return {k.decode(): v.decode() for k, v in data.items()}

    @classmethod
    def hexists(cls, key, field):
        """Check if field exists in hash key."""
        if cls._client is None:
            cls.configure()
        return cls._client.hexists(key, field)

    @classmethod
    def hdel(cls, key, *fields):
        """Delete one or more fields from hash key."""
        if cls._client is None:
            cls.configure()
        return cls._client.hdel(key, *fields)
    
    # -------- OTHER METHODS --------

    @classmethod
    def clean(cls):
        """Flush all data in the current Redis database."""
        if cls._client is None:
            cls.configure()
        cls._client.flushdb()
