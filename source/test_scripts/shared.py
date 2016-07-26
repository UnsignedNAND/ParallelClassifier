import multiprocessing
import numpy

from utils.timer import timer

size = 10
t = numpy.zeros((size, size))
for x in range(size):
    t[x][x] = x


class Proc(multiprocessing.Process):
    def __init__(self, idp):
        self.idp = idp
        super(self.__class__, self).__init__()

    def run(self):
        t[0][0] = 100.0
        print(id(t))


@timer
def test(process_num):
    global t
    processes = []
    for pid in range(process_num):
        p = Proc(pid)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    print(id(t))
    print(t)

if __name__ == '__main__':
    print('This scripts proves that when reading every process has access to '
          'the same instance in memory and that any write happening inside of '
          'a process is not copied to the shared memory')
    test(2)
