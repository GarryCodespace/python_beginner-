# Write a program which will find all such numbers which are divisible by 7 
# but are not a multiple of 5, between 2000 and 3200 (both included).
# The numbers obtained should be printed in a comma-separated sequence on a single line.

# modulo by 7 while not multiple of 5

result = []

for number in range(2000, 3201):
    if number % 7 == 0 and number % 5 != 0:
        result.append(number)


print(result)





