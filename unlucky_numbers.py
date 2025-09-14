for num in range(1,21):
    if num == 4 and num == 13:
        state = 'Unlucky'
    elif num % 2 == 0:
        state = 'Even'
    else:
        state = 'Odd'
    print(f"{num} is {state}")