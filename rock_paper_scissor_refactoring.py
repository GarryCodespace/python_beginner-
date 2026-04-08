import random
#Ask user Rock paper scissors
# if not rps invalid choise 
# print error 
# let the computer make a choice
# Print choices (emojis)
# Determine the winner
# Ask the user if they want to continue
# if not 
# terminate game 

def get_user_choice():
    while True:
        result = input('rock, paper, scissors? (r/p/s): ').lower()

        if(result not in choices):
            print('Invalid choice')
            continue
        else:
            break
    return result


choices = ('r', 'p', 's')

while True:
    result = input('rock, paper, scissors? (r/p/s): ').lower()

    if(result not in choices):
        print('Invalid choice')
        continue

    computer_choice = random.choice(choices)

    print(f'You choose {result}')

    print(f'computer choose {computer_choice}')

    if(result == choices):
        print('draw')
    elif((result == 'r' and computer_choice == 's') or
          (result == 'r' and computer_choice == 's') or
          (result == 'r' and computer_choice == 's')):
        print('you win')
    else:
        print('you lose')

    should_continue = input('Continue? (y/n): ').lower()
    if(should_continue == 'y'):
        continue
    else:
        break

