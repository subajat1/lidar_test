def fizz_buzz():
    for n in range(1,101):
        if n%5 == 0 and n%3 == 0:
            print('FizzBuzz!')
        elif n%5 == 0:
            print('Buzz')
        elif n%3 == 0:
            print('Fizz')
        else:
            print(str(n))
    return

fizz_buzz()