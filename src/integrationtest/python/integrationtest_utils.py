import os
import shutil


def readfile(resource_filename, script_filename):
    script_name, ext = os.path.splitext(os.path.basename(script_filename))
    return open(
        os.path.join(os.path.dirname(script_filename), 'resources/{}/{}'.format(script_name, resource_filename)))


def filepath(resource_filename, script_filename):
    script_name, ext = os.path.splitext(os.path.basename(script_filename))
    return os.path.join(os.path.dirname(script_filename), 'resources/{}/{}'.format(script_name, resource_filename))


def mongodb_test_url():
    if 'MONGO_TEST_URL' in os.environ:
        return os.environ['MONGO_TEST_URL']
    return None


def redis_test_url():
    if 'REDIS_TEST_URL' in os.environ:
        return os.environ['REDIS_TEST_URL']
    return None


def redis_test_port():
    if 'REDIS_TEST_PORT' in os.environ:
        return os.environ['REDIS_TEST_PORT']
    return "6379"


def is_storage_exists():
    return shutil.which('mongod') or mongodb_test_url()


def is_event_queue_exists():
    return shutil.which('redis-server') or redis_test_url()
