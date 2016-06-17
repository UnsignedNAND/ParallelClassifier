import multiprocessing
import time


class Process1(multiprocessing.Process):
    def __init__(self, lock):
        self.lock = lock
        super(self.__class__, self).__init__()

    def run(self):
        print('Process1 start')
        i = 0
        self.lock.acquire()
        while i < 10:

            i += 1
            print('Process1 inc', i)
            time.sleep(1)
        self.lock.release()


class Process2(multiprocessing.Process):
    def __init__(self, lock):
        self.lock = lock
        super(self.__class__, self).__init__()

    def run(self):
        print('Process2 start')
        i = 0
        while i < 10:
            self.lock.acquire()
            i += 1
            self.lock.release()
            print('Process2 inc', i)
            time.sleep(1)


if __name__ == '__main__':
    lock = multiprocessing.Lock()

    p1 = Process1(lock)
    p2 = Process2(lock)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
