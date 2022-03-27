import os


def to_dict_recursively(object):
    # objects with a __dict__ next
    if hasattr(object, '__dict__'):
        return to_dict_recursively(getattr(object, '__dict__'))
    # plain dicts
    if isinstance(object, dict):
        return {key: to_dict_recursively(value) for key, value in object.items()}
    # lists
    if isinstance(object, list):
        return [to_dict_recursively(element) for element in object]
    # primitive types
    return object


def camel_case_keys_recursively(object):
    if isinstance(object, dict):
        return {to_camel_case(key): camel_case_keys_recursively(value) for key, value in object.items()}
    if isinstance(object, list):
        return [camel_case_keys_recursively(element) for element in object]
    # primitive types
    return object


def to_camel_case(snake_case_identifier):
    parts = snake_case_identifier.split('_')
    parts = [part.capitalize() if index else part for index, part in enumerate(parts)]
    return ''.join(parts)


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None


def find_frame_path(filename: str) -> str:
    # Find the file in static dir or a subdirectory
    here = os.path.dirname(os.path.abspath(__file__))
    hti_static_dir = os.path.join(here, '..', 'static')
    return find_file(filename, hti_static_dir)
