from itertools import islice, tee, cycle

nwise = lambda g, n: zip(*(islice(g,i, None) for i, g, in enumerate(tee(g,n))))

every = lambda g, n: zip(g, cycle([True] + [False] * (n-1)))