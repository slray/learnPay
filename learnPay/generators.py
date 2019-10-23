from itertools import islice, tee

nwise = lambda g, n: zip(*(islice(g,i, None) for i, g, in enumerate(tee(g,n))))