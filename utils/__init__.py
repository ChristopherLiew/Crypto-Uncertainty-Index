import time
from functools import wraps


def timer(f):
    @wraps(f)
    def func(*args, **kwargs):
        tic = time.time()
        result = f(*args, **kwargs)
        print(f"Function `{f.__name__}` took: {time.time() - tic} seconds")
        return result
    return func
