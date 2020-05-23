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
