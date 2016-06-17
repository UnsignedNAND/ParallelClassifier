import multiprocessing
import time


class Process1(multiprocessing.Process):
    def __init__(self, pipes):
        self.pipes = pipes
        super(self.__class__, self).__init__()

    def run(self):
        print('Process1 start')
        for i in range(10):
            for pipe in self.pipes:
                pipe.send(i)
            print('Process1 send', i)
            time.sleep(1)


class Process2(multiprocessing.Process):
    def __init__(self, pipe):
        self.pipe = pipe
        super(self.__class__, self).__init__()

    def run(self):
        print('Process2 start')
        while True:
            val = self.pipe.recv()
            print(self.pid, 'received', val)
            if val == 9:
                break


if __name__ == '__main__':
    processes = 2
    pipes = []
    for pid in range(processes):
        pipe_parent, pipe_child = multiprocessing.Pipe()
        pipes.append((pipe_parent, pipe_child))

    p1 = Process1([pipe_parent for (pipe_parent, pipe_child) in pipes])

    ps = []
    for (pipe_parent, pipe_child) in pipes:
        ps.append(Process2(pipe_child))

    p1.start()
    for p in ps:
        p.start()

    p1.join()
    p1.join()
    for p in ps:
        p.join()
