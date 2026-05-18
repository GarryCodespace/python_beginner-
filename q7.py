# Question 7
# Question:
# _Write a program which takes 2 digits, X,Y as input and generates a 2-dimensional array. The element value in the i-th row and j-th column of the array should be i _ j.*

# Note: i=0,1.., X-1; j=0,1,¡­Y-1. Suppose the following inputs are given to the program: 3,5

# Then, the output of the program should be:

# [[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8]]
# Hints:
# Note: In case of input data being supplied to the question, it should be assumed to be a console input in a comma-separated form.
import random

raw_input = input("Give 2 digits: ")

raw_input = raw_input.split(",")

number_input = []
for i in raw_input:
    number = int(i)
    number_input.append(number)

result = []
for i in range(number_input[0]):
    row = []
    for j in range(number_input[1]):
        row.append(i*j)

    result.append(row)

print(result)
    







