import timeit


def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = timeit.default_timer()
        func_return = func(*args, **kwargs)
        time_elapsed = timeit.default_timer() - time_start
        print args, kwargs, time_elapsed
        return func_return

    return func_wrapper
