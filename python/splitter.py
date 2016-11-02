# Splitter
# Creator: Veini Lehkonen, lehkonev@gmail.com
# Version: 0.1
# Date: 2016-11-02
# ----------------------------------------------------------------------------
# Environment used to create and test:
# PyCharm Community Edition 2016.2.3
# Build #PC-162.1967.10, built on September 7, 2016
# JRE: 1.8.0_112-release-b343 x86
# JVM: OpenJDK Server VM by JetBrains s.r.o
# Python 3.5.2
# Windows 10 Home 64-bit
##############################################################################
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
