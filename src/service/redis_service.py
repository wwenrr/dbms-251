import redis
import json
import logging

logger = logging.getLogger(__name__)

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
    
    # Simple Redis SET/GET for JSON data
    @classmethod
    def json_set(cls, key, data):
        if cls._client is None:
            cls.configure()
        try:
            cls._client.execute_command('JSON.SET', key, '$', json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to JSON.SET key {key}: {e}")
            raise e
            

    @classmethod
    def json_get(cls, key, path='$'):
        if cls._client is None:
            cls.configure()
        try:
            result = cls._client.get(key)
            if result:
                return json.loads(result)
            return None
        except Exception as e:
            logger.error(f"Failed to GET key {key}: {e}")
            raise e

    @classmethod
    def clean(cls):
        if cls._client is None:
            cls.configure()
        cls._client.flushdb()

    @classmethod
    def create_index(cls):
        if cls._client is None:
            cls.configure()
        
        # Simple Redis without RediSearch - just log that we're using basic Redis
        logger.info("Using basic Redis without RediSearch module")
        return True
