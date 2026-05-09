#efine a class which has at least two methods:
#getString: to get a string from console input
#printString: to print the string in upper case.
#Also please include simple test function to test the class methods.
    
class ClassName:
    def __init__(self):
        self.string = ""

    def getString(self):
        self.string = input("get a string: ")

    def printString(self):
        self.string = self.string.upper()
        print(self.string)

class_name = ClassName()

class_name.getString()
class_name.printString()




        
        