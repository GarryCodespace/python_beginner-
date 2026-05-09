# Write a program which can compute the factorial of a given numbers.The results should be printed in a comma-separated sequence on a single line.Suppose the following input is supplied to the program: 8 Then, the output should be:40320

number = int(input("What is the factorial number: "))

final = 1

for i in range(number):
    final = final * (number - i)

print(final)



