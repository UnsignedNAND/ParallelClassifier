from multiprocessing import Process, Array
import timeit


def coord_2d_to_1d(col, row, items):
    return col + row * items


class Proc3(Process):
    def __init__(self, a, idp, shift, items):
        self.a = a
        self.idp = idp
        self.shift = shift
        self.items = items
        super(self.__class__, self).__init__()

    def run(self):
        row = self.idp
        while row < self.items:
            for col in range(row):
                self.a[coord_2d_to_1d(col, row, self.items)] = self.idp
            row += self.shift


if __name__ == '__main__':
    items = 10
    proc_num = 4
    arr = Array('i', items*items)

    t_start = timeit.default_timer()
    ps = []
    for idp in range(proc_num):
        p = Proc3(arr, idp, proc_num, items)
        p.start()
        ps.append(p)

    for p in ps:
        p.join()

    t_end = timeit.default_timer()
    s = ''
    c = 1
    for i in range(len(arr)):
        s += '{:>4}'.format(arr[i])
        if c % items == 0:
            print(s)
            s = ''
        c += 1

    print('Took', t_end-t_start)
