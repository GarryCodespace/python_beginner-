# Write a program that accepts a sentence and calculate the number of letters and digits.

# Suppose the following input is supplied to the program:

# hello world! 123
# Then, the output should be:

# LETTERS 10
# DIGITS 3

sentence = input("sentence: ").strip(" ")

count_number = 0

count_letter = 0

for i in sentence:
    if i.isdigit():
        count_number += 1
    
    elif i.isalpha():
        count_letter += 1

print(count_letter)

print(count_number)
        
