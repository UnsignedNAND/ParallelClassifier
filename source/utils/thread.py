import threading
import inspect
from logger import get_logger

logger = get_logger()


class Thread(threading.Thread):
    obj = None

    def __init__(self, obj=None):
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        if inspect.isfunction(self.obj):
            logger.info('Starting function thread')
            self.obj()
        elif inspect.isclass(self.obj) and hasattr(self.obj, 'start'):
            logger.info('Starting object thread')
            instance = self.obj()
            instance.start()
        elif inspect.isclass(self.obj):
            logger.error('Object passed to thread should implement "start" method!')
        else:
            logger.error('Thread is empty!')
            raise Exception('Thread is empty!')

if __name__ == '__main__':
    def test_function():
        print 'hello'


    class TestClass(object):
        def start(self):
            print 'tc hello'

    t1 = Thread(obj=test_function)
    t1.start()
    t1.join()

    t2 = Thread(obj=TestClass)
    t2.start()
    t2.join()
