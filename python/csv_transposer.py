# This doesn’t work properly yet, but if works well enough.
# Faults:
# If input has an empty row,it isn’t inserted into the not per_table output
# (bad), and an empty row is inserted into the per_table output (good).
# If input has a row with empty values, the empty values are inserted in the
# not per_table output (good), and an empty row is inserted in the
# per_table output (bad or neutral – should it also be empty values?).
# This file was wiped clean for unknown reasons and it was why I made this
# repository. I am slightly bitter.

import csv


def main(filename, outfile, per_table=True):
    csvlist = []
    first = True
    read_amount = 8

    with open(filename, newline='') as csvfile:
        sniffed_dialect = csv.Sniffer().sniff(csvfile.read(read_amount))
        print(sniffed_dialect)
        csvfile.seek(0)
        csvreader = csv.reader(csvfile, sniffed_dialect, delimiter=';')
        table = []
        ignore_first = 0
        row_number = 1

        for row in csvreader:
            print(row_number, "".join(row))
            row_number += 1
            if per_table and ("".join(row) == ""):
                print("tyhjä")
                csvlist.append(table)
                table = []
                table.append([])
                first = True
                ignore_first = 1

            elif not first:
                i = 0 + ignore_first
                for item in row:
                    print(i, item, end='')
                    if i == len(table):
                        table.append([])
                    table[i].append(item)
                    i += 1
                    print(i)
            else:
                for itemf in row:
                    tablef_row = []
                    tablef_row.append(itemf)
                    table.append(tablef_row)
                first = False

        csvlist.append(table)

        with open(outfile, 'w', newline='') as csvout:
            csvwriter = csv.writer(csvout, dialect=sniffed_dialect, delimiter=';')
            for result_table in csvlist:
                for roww in result_table:
                    csvwriter.writerow(roww)


main("csv_transposer_input.csv", "csv_transposer_output.csv", False)
main("csv_transposer_input.csv", "csv_transposer_output_per_table.csv", True)
