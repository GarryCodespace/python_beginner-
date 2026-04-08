import random 
#loop

#Ask for user for random number between 1 to 100:
number = random.randint(1, 100)

while True:
    try:    
        guess = int(input('guess the number between 1 and 100 '))
    #if the number is invalid 
    # output please enter a valid number
    #if number is higher than expected
    #output too high
        if guess > number:
            print('output too high')

    #if number is lower than expected 
        elif guess < number:
            print('output too low')
    # output too low
    # if correct
        else:
            print('Congrats you guessed the number')
            break
    #output Congrats you guessed the number 
    except ValueError:
        print('Please enter a valid number') 


