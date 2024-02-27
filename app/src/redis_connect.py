import os
import redis

## redis param connect
HOST_REDIS = os.getenv("HOST_REDIS")
PORT_REDIS = os.getenv("PORT_REDIS", 6379)
REDIS_PASS = os.getenv("REDIS_PASS")

def write_to_redis(keys_redis, time_last_successful):
    # Подключаемся к Redis
    r = redis.StrictRedis(host=HOST_REDIS, port=int(PORT_REDIS), password=REDIS_PASS, decode_responses=True)

    # Записываем данные в Redis
    #keys_redis = "last_successful"
    keys_redis = keys_redis
    r.set(keys_redis, time_last_successful)    

    return 'redis data send' 

def read_from_redis(keys_redis):
    # Подключаемся к Redis
    r = redis.StrictRedis(host=HOST_REDIS, port=int(PORT_REDIS), password=REDIS_PASS, decode_responses=True)

    keys_redis = keys_redis
    values_redis = r.get(keys_redis)

    return values_redis
