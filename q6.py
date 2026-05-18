# Write a program that calculates and prints the value according to the given formula:

# Q = Square root of [(2 _ C _ D)/H]

# Following are the fixed values of C and H:

# C is 50. H is 30.

# D is the variable whose values should be input to your program in a comma-separated sequence.For example Let us assume the following comma separated input sequence is given to the program:

import math

c = 50

h = 30

numbers = input("numbers: ")

array = numbers.split(",")

numbers = []

for item in array:
    numbers.append(int(item))

formula = []

for i in range(len(numbers)):
    Q = math.sqrt(2*c*numbers[i]/h)
    formula.append(Q)

print(formula)








