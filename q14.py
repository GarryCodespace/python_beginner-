# Write a program that accepts a sentence and calculate the number of upper case letters and lower case letters.

# Suppose the following input is supplied to the program:

# Hello world!
# Then, the output should be:

# UPPER CASE 1
# LOWER CASE 9

sentence = input("sentence: ").strip()


uppercase = 0

lowercase = 0

for i in sentence:
    if i.isupper():
        uppercase += 1
    elif i.islower():
        lowercase += 1

print("uppercase:", uppercase)

print("lowercase:", lowercase)
