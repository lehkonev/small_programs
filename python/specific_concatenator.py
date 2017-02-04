# Specific Concatenator
# Creator: Veini Lehkonen, lehkonev@gmail.com
# Version: 0.1
# Date: 2016-10-22
# ----------------------------------------------------------------------------
# Environment used to create and test:
# PyCharm Community Edition 2016.2.3
# Build #PC-162.1967.10, built on September 7, 2016
# JRE: 1.8.0_112-release-b343 x86
# JVM: OpenJDK Server VM by JetBrains s.r.o
# Python 3.5.2
# Windows 10 Home 64-bit
##############################################################################
# Reads a file (filename defined in conc_file) that defines a concatenation
# that should be performed on each newline-separated value found in the file
# defined in input_file.

ENC = "utf8"


def specific_concatenator(conc_file ="specific_concatenator.txt",
                          input_file = "specific_concatenator_input.txt",
                          output_file = "specific_concatenator_output.txt",
                          conc_comment = "#",
                          input_comment = "",
                          variable = "$$$$$",
                          separator = "\n\n",
                          write_mode = 'w',  # w: truncate, x: fail if exists.
                          encoding_concatenation = ENC,
                          encoding_input = ENC,
                          encoding_output = ENC):

    listing = read_file(conc_file, conc_comment, encoding_concatenation)
    listing_input = read_file(input_file, input_comment, encoding_input)

    if (len(listing) != 0) and (len(listing_input) != 0):
        write_file(output_file,
                   listing, listing_input,
                   variable, separator,
                   write_mode, encoding_output)


# Finds and replaces intentional newlines (\\n) in the input string (str)
# with proper newlines (\n) and returns the result.
# This should be done to all escape characters.
def escape_character_fix(str):
    found = str.find("\\n")
    while found != -1:
        str = str[:found] + "\n" + str[found+2:]
        found = str.find("\\n")
    return str


# Removes a possible ending newline from the input string (str)
# and returns it.
def remove_end_newline(str):
    if str[-1:] == "\n":
        str = str[:-1]
    return str


def read_file(filename, comment_mark, file_encoding):
    listing = []
    with open(filename, 'r', encoding=file_encoding) as filereading:
        for line in filereading:
            if not ((line == "\n") or (line == "")):
                if not (line[0] == comment_mark):
                    line = remove_end_newline(line)
                    line = escape_character_fix(line)
                    listing.append(line)

    return listing


def write_file(filename, concatenations, input_list, variable, separator,
               write_mode, encoding_output):
    with open(filename, write_mode, encoding=encoding_output) as new_file:
        new_file.write(concatenate(concatenations, input_list, variable,
                                   separator))


# This function is best explained with an example.
# Example concatenations: ["1", variable, "2 ", "3", variable, "4"]
# Example input: ["first", "second"]
# Example result_list: ["1first2 3first4", "1second2 3second4"]
# Returns a string joined from the values of result_list, using separator as
# separator.
def concatenate(concatenations, input, variable, separator):
    result_list = []
    for value in input:
        concatenation = ""
        for piece in concatenations:
            if piece != variable:
                concatenation += piece
            else:
                concatenation += value
        result_list.append(concatenation)
    return separator.join(result_list)


#specific_concatenator()
specific_concatenator("c.txt", "c_input.txt", "c_output.txt")
