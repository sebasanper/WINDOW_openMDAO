def thomas(a, b, c, d):
    """Uses Thomas algorithm for solving a tridiagonal matrix for n unknowns.
     a, b, and  are a list of the matrix entries
     Matrix form of:
     [b1 c1    ] [x1] [d1]
     |a2 b2 c2   | |x2|  |d2|
     | a3 b3 c3  | |x3|  |d3|
     |     | |' |= | '|
     |     | |' |  | '|
     [   an bn cn] |xn] [dn]
    """
    # Finding the size of the matrix and determine n
    cdef int n, i, j
    n = len(b)
    # print n # Used for debugging
    # Test the size of a and c
    if len(a) != n - 1:
        # print 'Wrong index size for a.\n A should have an index of', n - 1, '\n Your a has ', len(a)
        exit()
    if len(c) != n - 1:
        # print 'Wrong index size for c.\n C should have an index of', n - 1, '\n Your c has', len(c)
        exit()

    # Converting to float and appending 0.0 to c
    for i in range(0, len(a)):
        a[i] = float(a[i])
    for i in range(0, len(b)):
        b[i] = float(b[i])
    for i in range(0, len(c)):
        c[i] = float(c[i])
    for i in range(0, len(d)):
        d[i] = float(d[i])
    c.append(0.0)  # Hack to make the function to work

    # Calculate p and q
    p = []
    q = []
    p.append(c[0] / b[0])
    q.append(d[0] / b[0])
    for j in range(1, n):
        # print 'thomas algorithm'
        # print j, b[j], c[j], p[j - 1]
        # print
        pj = c[j] / (b[j] - a[j - 1] * p[j - 1])
        qj = (d[j] - a[j - 1] * q[j - 1]) / (b[j] - a[j - 1] * p[j - 1])
        p.append(pj)
        q.append(qj)
    # print p,q # Used for debugging the code!

    # Back sub
    x = [q[n - 1]]
    for j in range(n - 2, -1, -1):
        xj = q[j] - p[j] * x[0]  # Value holder
        x.insert(0, xj)  # Building the list backwards

    # Return the value
    return x

if __name__ == '__main__':
    a = [1.0 for _ in range(30)]
    b = [2.0 for _ in range(31)]
    c = a
    d = [x for x in range(1, 17)] + [(16 - x) for x in range(1, 16)]
    x = thomas(a, b, c, d)
    # print x
