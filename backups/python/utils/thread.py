import threading
import inspect
from logger import get_logger

_LOG = get_logger()


class Thread(threading.Thread):
    obj = None

    def __init__(self, obj=None):
        threading.Thread.__init__(self)
        self.obj = obj

    def run(self):
        if inspect.isfunction(self.obj):
            _LOG.info('Starting function thread')
            self.obj()
        elif inspect.isclass(self.obj) and hasattr(self.obj, 'start'):
            _LOG.info('Starting object thread')
            instance = self.obj()
            instance.start()
        elif inspect.isclass(self.obj):
            _LOG.error('Object passed to thread should implement "start" method!')
        else:
            _LOG.error('Thread is empty!')
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
