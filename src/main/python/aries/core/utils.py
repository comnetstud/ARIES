"""Helpers for simulation process"""
import os

import redis
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from aries.core.exceptions import FilePathNotFoundError, AriesException, ValidationError


def check_if_mongodb_is_running(mongodb_uri):
    """Check if Mongo DB server is running and return back initialized mongodb client"""
    try:
        client = MongoClient(mongodb_uri)
        client.admin.command('ismaster')
        return client
    except ConnectionFailure as e:
        raise AriesException("MongoDB is not available on this URI : {}".format(mongodb_uri)) from e


def check_if_redis_is_running(host, port):
    """Check if redis server is running and return back initialized redis client"""
    try:
        client = redis.Redis(host, port)
        client.client_list()
        return client
    except redis.ConnectionError as e:
        raise AriesException("Redis is not available on this host and port : {}:{}".format(host, port)) from e


def check_if_file_exists(file_path):
    """Check if file exists and return back opened file connection"""
    if os.path.isfile(file_path):
        return open(file_path, 'r')
    else:
        raise FilePathNotFoundError("Could not find file '{}' ".format(file_path))


def validate(obj, obj_type, validator):
    """Validate object according to provided validator"""
    validation_state = validator.validate(obj)
    if not validation_state:
        raise ValidationError("{} is not valid. Please take a look to these field(s) : {}"
                              .format(obj_type, str(validator.errors)))
    else:
        return validation_state

def validate_log_level(level):
    try:
        logging._checkLevel(level)
    except TypeError as e:
        print(e)
