import random 
# loop
    #Ask :roll the dice
    # If user enters y 
    # generate 2 random numbers in a dice 1-6
    #print them
    # If user enters n 
    #print thank you message
    # terminate
    # else 
    # print invalid choice 

while True:
    user_input = input('Roll the dice y/n? ').lower()

    if user_input == 'y':
        random1 = random.randint(1,6)
        random2 = random.randint(1,6)
        print(f"{random1} {random2}")

    elif user_input == 'n':
        print('Thank you')
        break

    else:
        print('invalid')
    






