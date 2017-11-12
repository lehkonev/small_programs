def main():
    words = {}

    print("Input words separated by newline. Enter an empty line to stop.")

    continuing = True
    while continuing:
        row = input()

        if row =="":
            continuing = False

        else:
            word_list = row.split()
            for word in word_list:
                word = word.lower()
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1

    for word in sorted(words):
        print(word + ":", words[word])


main()
