def nth_square(n):
    if n == 1:
        return 1
    elif n > 1:
        square = list(range(1, n+1))
        n_square = [n*n for n in square]
        sum_nth = sum(n_square)
        return sum_nth
    else:
        return 'invalid input error, we require positive integer as input'

print(nth_square(5))