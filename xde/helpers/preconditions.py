def check_not_none(reference, message=None):
    if reference is None:
        raise ValueError(message or 'None value.')
    return reference


def check_not_empty(reference, message=None):
    if not reference:
        raise ValueError(message or 'Empty value.')
    return reference


def check_type(reference, type, message=None):
    if not isinstance(reference, type):
        raise ValueError(message or 'Value must be an instance of %s' % type)
    return reference


def check_string(reference, message=None):
    return check_type(reference, basestring, message)
