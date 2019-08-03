from __future__ import absolute_import

import types

from collections import Sequence

__author__ = 'duydo'


def remove_skip_values(obj, skip_values=(None, [], {})):
    """Remove None values from the given object."""
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_skip_values(x) for x in obj if x not in skip_values)
    elif isinstance(obj, dict):
        return type(obj)((k, remove_skip_values(v))
                         for k, v in obj.items() if v not in skip_values)
    else:
        return obj


def value_of(d, key, default=None):
    """Return value of key in form of x.y.z from a dict d"""
    if '.' in key:
        keys = key.split('.')
        v = dict(d)
        for key in keys:
            if isinstance(v, dict):
                v = v.get(key)
            else:
                return default
        return v
    return d.get(key, default)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def is_sequence(value):
    return (is_generator(value) or
            (isinstance(value, Sequence) and not isinstance(value, basestring)))


def is_generator(value):
    """Return whether `value` is a generator or generator-like."""
    return (isinstance(value, types.GeneratorType) or
            (hasattr(value, '__iter__') and hasattr(value, '__next__') and
             not hasattr(value, '__getitem__')))


class CaseInsensitiveDict(dict):
    """Basic case insensitive dict with strings only keys."""

    def __init__(self, a_dict=None):
        super(CaseInsensitiveDict, self).__init__()
        if a_dict:
            for k, v in a_dict.items():
                self[k.lower()] = v

    def __contains__(self, k):
        return super(CaseInsensitiveDict, self).has_key(k.lower())

    def __delitem__(self, k):
        super(CaseInsensitiveDict, self).__delitem__(k.lower())

    def __getitem__(self, k):
        return super(CaseInsensitiveDict, self).__getitem__(k.lower())

    def get(self, k, default=None):
        key = k.lower()
        return self[key] if key in self else default

    def __setitem__(self, k, v):
        super(CaseInsensitiveDict, self).__setitem__(k.lower(), v)
