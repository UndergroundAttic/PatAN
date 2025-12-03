import time
from functools import wraps


def elapsed(func):
    """
    Decorator that calculates and prints the elapsed time of a function.

    Args:
        func: The function to be timed

    Returns:
        The wrapped function that measures execution time
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} executed in {elapsed_time:.4f} seconds")
        return result

    return wrapper
