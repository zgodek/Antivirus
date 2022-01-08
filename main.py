from scan import full_scan, quick_scan, when_to_scan


def main():
    anwser = ""
    while anwser != "4":
        anwser = input("Type:\n1 for full scan\n2 for quick scan\n3 to set the time when to perform a quick scan\n4 to shut down the program\n")
        if anwser == "1":
            path = input("Enter the path:\n")
            print(full_scan(path))
        elif anwser == "2":
            path = input("Enter the path:\n")
            print(quick_scan(path))
        elif anwser == "3":
            time = input("Enter the time in this format: hour:min:sec\n")
            when_to_scan(time)
        else:
            continue
    return


if __name__ == "__main__":
    main()
