import math
import multiprocessing
import timeit

PROC_NUM = 2
ELEMENTS = 1000 * 10


def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = timeit.default_timer()
        func_return = func(*args, **kwargs)
        time_elapsed = timeit.default_timer() - time_start
        print('Function \'{0}\' took {1:5.3} s to finish'.format(
            func.__name__,
            time_elapsed)
        )
        return func_return

    return func_wrapper


@timer
def test_manager():
    class ManagerProcess(multiprocessing.Process):
        def __init__(self, d, offset, shift, limit):
            super(self.__class__, self).__init__()
            self.d = d
            self.offset = offset
            self.shift = shift
            self.limit = limit

        def run(self):
            item = self.offset
            while True:
                if item > self.limit:
                    break
                self.d[item] = item
                item += self.shift

    manager = multiprocessing.Manager()
    d = manager.dict()
    ps = []
    for i in range(PROC_NUM):
        p = ManagerProcess(d=d, shift=PROC_NUM, offset=i, limit=ELEMENTS)
        p.start()
        ps.append(p)

    for p in ps:
        p.join()


@timer
def test_single_pipe():
    # sends single items through pipe
    class PipeSingleProcess(multiprocessing.Process):
        def __init__(self, pipe, offset, shift, limit):
            super(self.__class__, self).__init__()
            self.pipe = pipe
            self.offset = offset
            self.shift = shift
            self.limit = limit

        def run(self):
            item = self.offset
            while True:
                if item > self.limit:
                    break
                self.pipe.send(item)
                item += self.shift
            self.pipe.send(None)

    ps = []
    pipe_parent, pipe_child = multiprocessing.Pipe()
    for i in range(PROC_NUM):
        p = PipeSingleProcess(pipe=pipe_child, shift=PROC_NUM, offset=i,
                              limit=ELEMENTS)
        p.start()
        ps.append(p)
    results = {}

    not_finished = PROC_NUM
    while not_finished:
        recv = pipe_parent.recv()
        if recv is None:
            not_finished -= 1
            continue
        results[recv] = recv

    for p in ps:
        p.join()


@timer
def test_single_queue():
    # sends single items through pipe
    class PipeSingleQueue(multiprocessing.Process):
        def __init__(self, queue, offset, shift, limit):
            super(self.__class__, self).__init__()
            self.queue = queue
            self.offset = offset
            self.shift = shift
            self.limit = limit

        def run(self):
            item = self.offset
            while True:
                if item > self.limit:
                    break
                self.queue.put(item)
                item += self.shift
            self.queue.put(None)

    ps = []
    queue = multiprocessing.Queue()
    for i in range(PROC_NUM):
        p = PipeSingleQueue(queue=queue, shift=PROC_NUM, offset=i,
                            limit=ELEMENTS)
        p.start()
        ps.append(p)
    results = {}

    not_finished = PROC_NUM
    while not_finished:
        recv = queue.get()
        if recv is None:
            not_finished -= 1
            continue
        results[recv] = recv

    for p in ps:
        p.join()

def main():
    global PROC_NUM
    for i in range(1, 4+1):
        print('{0} {1} {0}'.format('-'*10, i))
        PROC_NUM = i
        test_manager()
        test_single_pipe()
        test_single_queue()


if __name__ == '__main__':
    main()
