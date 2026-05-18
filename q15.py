# Question:
# Write a program that computes the value of a+aa+aaa+aaaa with a given digit as the value of a.

# Suppose the following input is supplied to the program:

# 9
# Then, the output should be:

# 11106

number = input("number: ")

number1 = number + number

number2 = number1 + number

number3 = number2 + number

value = int(number) + int(number2) + int(number3) + int(number) 

print(value)


