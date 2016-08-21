import multiprocessing
import time


class ProcessX(multiprocessing.Process):
    def __init__(self, pipe):
        self.pipe = pipe
        super(self.__class__, self).__init__()

    def run(self):
        for i in range(5):
            self.pipe.send((self.pid, i))
            time.sleep(1)
        self.pipe.send(None)


class ProcessY(multiprocessing.Process):
    def __init__(self, pipe):
        self.pipe = pipe
        super(self.__class__, self).__init__()

    def run(self):
        r = 1
        while r:
            r = self.pipe.recv()
            print(r)


if __name__ == '__main__':
    x = 4

    print('Proof that more than one process can write to the same pipe')

    ps = []

    parent, child = multiprocessing.Pipe()

    for x in range(4):
        p = ProcessX(child)
        p.start()
        ps.append(p)

    kill = x
    while kill:
        r = parent.recv()
        if r is None:
            kill -= 1
            continue
        print(r)

    for p in ps:
        p.join()

    print('-'*20)

    print('Proof that only one process can read from the same pipe')

    ps = []

    parent, child = multiprocessing.Pipe()

    for x in range(4):
        p = ProcessY(child)
        p.start()
        ps.append(p)

    for i in range(5):
        parent.send(i)
        time.sleep(1)

    for p in ps:
        p.join()
