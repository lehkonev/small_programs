# Currency Unit Switcher
# Creator: Veini Lehkonen, lehkonev@gmail.com
# Version: 0.1
# Date: 2016-11-20
# ----------------------------------------------------------------------------
# Environment used to create and test:
# PyCharm Community Edition 2016.2.3
# Build #PC-162.1967.10, built on September 7, 2016
# JRE: 1.8.0_112-release-b343 x86
# JVM: OpenJDK Server VM by JetBrains s.r.o
# Python 3.5.2
# Windows 10 Home 64-bit
##############################################################################
# Reads a file (filename defined in input_file), searches it for occurrences of
# [number, separator 1, money unit] where:
#   * number is a real number or an integer,
#   * separator is a space or some other string and
#   * money unit is a money symbol or some other string.
# It then switches them around and forms [money unit, separator 2, number].
# For example, “5 €” becomes “€5”.

from splitter import splitter


def currency_unit_switcher(input_file="input.txt", output_file="output.txt",
                           integer=True, first_separator=" ",
                           second_separator="", symbol="€", encoding="utf8",
                           write_mode='a'):
    # w: truncate, x: fail if exists, a: append

    rows = read_file(input_file, encoding)

    if len(rows) != 0:
        number = 0
        number_string = ""
        number_found = False
        new_rows = []

        for row in rows:
            words = splitter(row, first_separator)
            new_words = []

            for word in words:
                if number_found:
                    if word == symbol:
                        new_words.append("{0}{1}{2}".format(
                            symbol, second_separator, number_string))
                        number_string = ""
                        number_found = False

                    else:
                        new_words.append("{0}".format(number_string))
                        number_found = False
                        number_string = ""
                        new_words.append(word)

                else:
                    try:
                        if integer:
                            number_string = word
                            number = int(word)
                            number_found = True
                        else:
                            number_string = word
                            number = float(word)
                            number_found = True
                    except ValueError:
                        number_found = False
                        number_string = ""
                        new_words.append(word)

            if number_found:
                new_words.append("{0}".format(number))

            new_rows.append(first_separator.join(new_words))

        # Rows are done.

        write_file(output_file, new_rows, write_mode, encoding)


def read_file(filename, file_encoding):
    listing = []
    with open(filename, 'r', encoding=file_encoding) as filereading:
        for line in filereading:
            listing.append(line)

    return listing


def write_file(output_file, new_rows, write_mode, encoding):
      #  filename, concatenations, input, variable, separator,
       #         write_mode, encoding_output):
    with open(output_file, write_mode, encoding=encoding) as new_file:
        for row in new_rows:
            new_file.write(row)


currency_unit_switcher(input_file="index.html", output_file="output.txt",
                       integer=False, first_separator=" ",
                       second_separator="", symbol="€", encoding="utf8",
                       write_mode='a')
