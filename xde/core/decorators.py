# Copyright (C) 2016 Xomad. All rights reserved.
#
# Created on 12/04/2016

from __future__ import print_function

import functools
import warnings


def deprecated(func):
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.
    """

    def new_func(*args, **kwargs):
        warnings.warn('Call to deprecated function %s.' % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


class handle_exceptions(object):
    func = None

    def __init__(self, exceptions, handler):
        self.exceptions = exceptions
        self.handler = handler

    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            return self.func
        try:
            return self.func(*args, **kwargs)
        except self.exceptions as exc:
            return self.handler(exc, *args, **kwargs)


class lazy_property(object):
    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)

    def __get__(self, obj, type_):
        if obj is None:
            return self
        val = self.function(obj)
        obj.__dict__[self.function.__name__] = val
        return val
