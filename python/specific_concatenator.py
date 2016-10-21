# Specific Concatenator
# Creator: Veini Lehkonen, lehkonev@gmail.com
##############################################################################
# Reads a file (name defined in FILENAME) that defines a concatenation that
# should be performed on each newline-separated value found in the file
# defined in INPUT_FILE.

FILENAME = "specific_concatenator.txt"
COMMENT_MARK = "#"
INPUT_FILE = "specific_concatenator_input.txt"
OUTPUT_FILE = "specific_concatenator_output.txt"
VARIABLE = "$$$$$"
SEPARATOR = "\n\n"
CLEAR_INPUT_FILE = False
OVERWRITE_OUTPUT_FILE = True


def main(filename):

    # Rewrite that.

    # new_filename = "k_" + filename
    # opnumlist = []
    #
    # with open(filename, 'r', encoding="utf8") as filename:
    #
    #     for line in filename:
    #         if line[-1:] == "\n":
    #             line = line[:-1]
    #         opnumlist.append(line)
    #
    #     with open(new_filename, 'w+', encoding="utf8") as new_filename:
    #         new_filename.write(new_file)


main(FILENAME)
