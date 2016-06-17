import multiprocessing
import time


class Process1(multiprocessing.Process):
    def __init__(self, event):
        self.event = event
        super(self.__class__, self).__init__()

    def run(self):
        print('Process1 start')
        self.event.clear()
        i = 0
        while i < 5:
            print('Process1 wait', i)
            i += 1
            time.sleep(1)
        self.event.set()


class Process2(multiprocessing.Process):
    def __init__(self, event):
        self.event = event
        super(self.__class__, self).__init__()

    def run(self):
        print('Process2 start')
        self.event.wait()
        i = 0
        while i < 5:
            print('Process', self.pid, 'progress', i)
            i += 1
            time.sleep(1)


if __name__ == '__main__':
    event = multiprocessing.Event()

    p1 = Process1(event)
    p2 = Process2(event)
    p3 = Process2(event)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
