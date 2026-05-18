def printlist():
    list = []
    for i in range(1,21):
        list.append(i ** 2)

    for i in range(1, 6):
        print(list[20-i])

printlist()
