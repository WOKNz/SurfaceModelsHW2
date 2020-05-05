def fast_sqrt(y, tolerance=0.06):
    prev = -1.0
    x = 1.0
    while abs(x - prev) > tolerance:  # within range
        prev = x
        x = x - (x * x - y) / (2 * x)
    return x

if __name__ == '__main__':
    print(fast_sqrt(2))