import os


def readfile(resource_filename, script_filename):
    script_name, ext = os.path.splitext(os.path.basename(script_filename))
    return open(
        os.path.join(os.path.dirname(script_filename), 'resources/{}/{}'.format(script_name, resource_filename)))


def check_if_properties_is_set(test, object_name, obj):
    test.assertIsNotNone(obj, "Object of {} type is not set".format(object_name))
    attributes = [i for i in dir(obj) if not callable(i) and not i.startswith("__")]
    for attr in attributes:
        test.assertIsNotNone(getattr(obj, attr),
                             "Attribute {} in object of '{}' type is not set".format(attr, object_name))

def check_if_properties_is_set_except(test, object_name, obj, except_properties=[]):
    test.assertIsNotNone(obj, "Object of {} type is not set".format(object_name))
    attributes = [i for i in dir(obj) if not callable(i) and not i.startswith("__")]
    for attr in attributes:
        if attr in except_properties:
            continue
        test.assertIsNotNone(getattr(obj, attr),
                             "Attribute {} in object of '{}' type is not set".format(attr, object_name))
