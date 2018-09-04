import pprint
import functools
from collections import defaultdict
import inspect


### dictionary ###

def invert(d, container=list, codomain=None):
    s = defaultdict(container)
    for k, v in d.items():
        s[v].append(k)
    # fill in range
    if codomain is not None:
        for v in codomain:
            s[v]
    return dict(s)


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
    HEADER = '\033[95m'  # red
    INCOMING = '\033[34m'  # blue
    OUTGOING = '\033[36m'  # green
    REGULAR = '\033[37m'  # light grey
    ENDC = '\033[0m'


def print_header(s):
    print(LColor.HEADER + s + LColor.ENDC)


def cprint(s, lcolor):
    print(lcolor + s + LColor.ENDC)


def logging(lcolor=LColor.REGULAR):
    """Return a decorator that logs the method call in the specified lcolor."""

    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            log = "===> calling '%s'" % method.__name__
            callargs = inspect.getcallargs(method, *args, **kwargs)
            if 'self' in callargs:
                log += " on %s" % callargs.pop('self')
            if callargs:
                log += " with args:"
            cprint(log, lcolor)
            if callargs:
                print(tree_dict(callargs))
            return method(*args, **kwargs)

        return wrapper

    return decorator


def compile_coffeescript(dir, output):
    """Compile coffeescripts in dir"""

    print_header("==> Compiling coffeescripts in %s into %s" % (dir, output))

    import coffeescript
    import os

    scripts = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        scripts.extend([os.path.join(dirpath, filename) for filename in filenames if filename.endswith('.coffee')])
    with open(output, 'w') as f:
        f.write(coffeescript.compile_file(scripts))
