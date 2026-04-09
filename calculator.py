while True:
    try:
        number1 = float(input("Whats your number1: "))
        number2 = float(input("Whats your number2: "))
    except ValueError:
        print("Invalid number. Try again.")
        continue

    operator = input("Whats the operator (+ - * /): ")

    if operator == "+":
        print(number1 + number2)

    elif operator == "-":
        print(number1 - number2)

    elif operator == "/":
        if number2 == 0:
            print("Cannot divide by zero")
        else:
            print(number1 / number2)

    elif operator == "*":
        print(number1 * number2)

    else:
        print("Invalid operator")

    again = input("Again? (y/n): ").lower()
    if again != "y":
        break



