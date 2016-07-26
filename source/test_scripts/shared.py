# import multiprocessing
# import numpy
#
# from utils.timer import timer
#
# size = 10
# t = numpy.zeros((size, size))
# for x in range(size):
#     t[x][x] = x
#
#
# class Proc(multiprocessing.Process):
#     def __init__(self, idp):
#         self.idp = idp
#         super(self.__class__, self).__init__()
#
#     def run(self):
#         t[0][0] = 100.0
#         print(id(t))
#
#
# class Proc2(multiprocessing.Process):
#     def __init__(self, idp, shift, arr):
#         self.idp = idp
#         self.shift = shift
#         self.arr = arr
#         super(self.__class__, self).__init__()
#
#     def run(self):
#         x = self.idp
#         while True:
#             if x < len(self.arr):
#                 break
#             self.arr[x] = self.idp
#             x += self.shift
#
#
# @timer
# def test1(process_num):
#     global t
#     processes = []
#     for pid in range(process_num):
#         p = Proc(pid)
#         p.start()
#         processes.append(p)
#
#     for p in processes:
#         p.join()
#     print(id(t))
#     print(t)
#
#
# def test2(process_num):
#     ra = multiprocessing.Array('d', 10)
#     print([val for val in ra])
#     ps = []
#     for pid in range(process_num):
#         p = Proc2(pid, process_num, ra)
#         p.start()
#         ps.append(p)
#
#     for p in ps:
#         p.join()
#
#     print([val for val in ra])
#
# if __name__ == '__main__':
#     print('This scripts proves that when reading every process has access to '
#           'the same instance in memory and that any write happening inside of '
#           'a process is not copied to the shared memory')
#     test2(2)


from multiprocessing import Process, Value, Array


class Proc3(Process):
    def __init__(self, n, a, idp, shift):
        self.n = n
        self.a = a
        self.idp = idp
        self.shift = shift
        super(self.__class__, self).__init__()

    def run(self):
        self.n.value = 3.1415927
        elems = len(self.a)
        start = self.idp
        c = 0
        while True:
            if start > elems-1:
                break
            # print(self.idp, start)
            self.a[start] = start**start
            start += self.shift
            c += 1
        print(self.idp, c)


if __name__ == '__main__':
    import timeit
    prcs = 4
    num = Value('d', 0.0)
    arr = Array('i', range(100*100))
    t_start = timeit.default_timer()
    ps = []
    for idp in range(prcs):
        p = Proc3(num, arr, idp, prcs)
        p.start()
        ps.append(p)

    for p in ps:
        p.join()

    print(num.value)
    t_end = timeit.default_timer()
    print('Took', t_end-t_start)
    # print(arr[:-1])
