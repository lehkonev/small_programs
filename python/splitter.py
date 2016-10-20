# This function splits the given string in the variable row into list items at
# the character in the variable split. If the variable empty is True, empty
# strings will be returned as well.
def splitter(row, split = " ", empty = True):
    word = ""
    list = []

    for letter in row:
        if letter == split:
            if (word != "") or empty:
                list.append(word)
                word = ""
        else:
            word += letter

    if (word != "") or empty:
        list.append(word)

    return list
