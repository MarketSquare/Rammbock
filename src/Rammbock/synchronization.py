import threading

from .decorator import decorator


LOCK = threading.RLock()


SYNCHRONIZATION = True


@decorator
def synchronized(f, *args, **kw):
    """ Synchronization decorator """
    if not SYNCHRONIZATION:
        return f(*args, **kw)
    with LOCK:
        return f(*args, **kw)


class SynchronizedType(type):

    def __new__(cls, name, bases, local):
        for name, item in local.items():
            if callable(item) and not name.startswith("_"):
                local[name] = synchronized(item)
        return type.__new__(cls, name, bases, local)
