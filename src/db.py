from flask import current_app,g
from redis import StrictRedis, ConnectionPool

def connect():
    pool = ConnectionPool(host='127.0.0.1', port=6379, db=0, password='')
    redis = StrictRedis(connection_pool=pool,encoding='utf-8',decode_responses=True)
    return redis
