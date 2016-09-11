import timeit
import logging

time_records = []

def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = timeit.default_timer()
        func_return = func(*args, **kwargs)
        time_elapsed = timeit.default_timer() - time_start
        # print args, kwargs, time_elapsed
        LOG = logging.getLogger('wiki')
        LOG.info('Function \'{0}\' took {1:5.3} s to finish'.format(
            func.__name__,
            time_elapsed)
        )
        time_records.append(
            (func.__name__, time_elapsed)
        )
        return func_return

    return func_wrapper
