# Define a function that can accept two strings as input and print the string with maximum length in console. If two strings have the same length, then the function should print all strings line by line.

# Hints:
# Use len() function to get the length of a string.

def find_maximum_string(a,b):
    if len(a) > len(b):
        return a
    else:
        return b

print(find_maximum_string("wwwww", "wwwwwwww"))