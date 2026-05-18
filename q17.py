# Write a program that computes the net amount of a bank account based a transaction log from console input. The transaction log format is shown as following:

# D 100
# W 200
# D means deposit while W means withdrawal.
# Suppose the following input is supplied to the program:

# D 300
# D 300
# W 200
# D 100
# Then, the output should be:

# 500

money = 0

while True:
    amount = input("Bank: ").split(" ")

    if amount[0] == "D":
        money = money + int(amount[1])
    elif amount[0] == "W":
        money = money - int(amount[1])
    elif amount[0] == "Q":
        break

print(money)
    
    



