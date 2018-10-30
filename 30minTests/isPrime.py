

def is_prime(n):

    if n < 2:
        return 'invalid input error, has to be greater than 1'
    elif n == 2:
        return True
    else:
        isPrime = True
        for i in range(2, n):
            if(n % i == 0):
                isPrime = False
        return isPrime

print(is_prime(26357))
