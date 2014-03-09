import pprint
import functools


### dictionary ###

def extract(d, *args, default=None):
    """Return a tuple of results extracted from the dictionary using strings of paths to the values

    E.g. extract(d, 'a', 'b.c') is will return (d.get(a), d.get(b).get(c)

    """

    assert isinstance(d, dict)
    results = []
    for key in args:
        key = key.split('.')
        result = d
        for attr in key:
            if not isinstance(result, dict):
                result = default
                break
            result = result.get(attr)
            if result is None:
                result = default
                break
        results.append(result)
    return tuple(results)


### logging helpers ###

def tree_dict(d, indent=4):
    return pprint.pformat(d, indent=indent)


class LColor(object):
    HEADER = '\033[95m'
    INCOMING = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OUTGOING = '\033[36m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def print_header(s):
    print(LColor.HEADER + s + LColor.ENDC)


def cprint(s, lcolor):
    print(lcolor + s + LColor.ENDC)


def logging(lcolor=LColor.OKGREEN):
    """Return a decorator that logs the method call in the specified lcolor."""

    def decorator(method):
        method_name = method.__name__

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            log = "===> calling function '%s'" % method_name
            try:
                method.__self__
            except AttributeError:
                pass
            else:
                log += " on %s" % method.__self__
            if args:
                log += " with args:"
            cprint(log, lcolor)
            if args:
                print(tree_dict(args))
            return method(*args, **kwargs)

        return wrapper

    return decorator
