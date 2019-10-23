
class Adder:
    def __init__(self,z=0):
        self.z = z
    def __call__(self, x, y):
        self.z += 1
        return x + y


from time import sleep

'''def compute(x):
    sleep(.1)
    return  x ** 2

class Process:
    def __init__(self, dataset):

       self.dataset = dataset

    def __iter__(self):
        self.dataset_iter = iter(self.dataset)
        return self

    def __next__(dataset):
        results = []
        for x in dataset:
            rv = compute(x)
            results.append(rv)
        return results

dataset = range(10)


for idx, x in enumerate(Process(dataset), start=1):
    print(x)
    if idx >= 3:
        break
'''

def fib(a=1, b=1):
    while True:
        yield a
        a , b = b, a + b

from itertools import islice, tee
for x in islice(fib(), 0):
    pass



nwise = lambda g, n: zip(*(islice(g,i, None) for i, g, in enumerate(tee(g,n))))


for x in nwise(range(10), 5):
    print(x)