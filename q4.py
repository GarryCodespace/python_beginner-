# Write a program which accepts a sequence of comma-separated numbers from console 
# and generate a list and a tuple which contains every number.Suppose the following input is supplied to the program:

number = input("input list of numbers with commas: ")

array = number.split(",")

tuplelist = tuple(array)

print(array)
print(tuplelist)




