# Question:
# Write a method which can calculate square value of number

# Hints:
# Using the ** operator which can be written as n**p where means n^p

class solution:
    def square(self, n):
        number = n ** 2
        return number

obj = solution()

k =int(input("number: "))

print(obj.square(k))
