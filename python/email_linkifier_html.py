# Makes HTML “mailto:” links out of bare email addresses.
# Assumes that emails and links are always on the same line without
# whitespace, like this: “<a href="mailto:xx@xx.xx">xx@xx.xx</a>”
# ---------------------------------------------------------------------------

import os
import re


# ---------------------------------------------------------------------------
# file_reader: Lukee minkä tahansa tiedoston.
# * Parametri filename: luettavan tiedoston nimi merkkijonona
# - Paluuarvo rows: tiedostosta luetut rivit listassa
def file_reader(filename):
    rows = []
    message = ""
    try:
        file = open(filename, 'r', encoding="UTF8")
        row = file.readline()
        while row != "":
            # Poistetaan rivinvaihto lopusta.
            # if row[-1] == '\n':
            #     row = row[:-1]
            rows.append(row)
            row = file.readline()
        file.close()
    except:
        message = "Error: Reading file {:s} failed.".format(filename)

    return rows, message


# ---------------------------------------------------------------------------
# file_writer: Kirjoittaa minkä tahansa tiedoston.
# * Parametri filename: luettavan tiedoston nimi merkkijonona
# * Parametri rows: tiedostosta luetut rivit listassa
def file_writer(directory, filename, rows, prefix="", suffix=""):
    message = ""
    filename = directory + "/" + prefix + filename + suffix
    try:
        file = open(filename, 'w', encoding="UTF8")
        file.writelines(rows)
        file.close()
    except:
        message = "Error: Writing file {:s} failed.".format(filename)

    return message


# ---------------------------------------------------------------------------
# file_list: returns a list of files of specified types from one directory.
# * Parameter filetype: what kind of files to look for. Empty list means
#   that all files are listed.
# * Parameter directory: files are searched from this directory.
# Return value
def file_list(filetypes, directory="."):
    filenames = os.listdir(directory)
    wanted_filenames = []

    if len(filetypes) == 0:
        wanted_filenames = filenames
    else:
        for filename in filenames:
            for filetype in filetypes:
                if filename[-len(filetype):] == filetype:
                    wanted_filenames.append(filename)

    return wanted_filenames


# ---------------------------------------------------------------------------
# Makes an email link.
def linkify(rows):
    changed = False

    for n in range(0, len(rows)):
        row = rows[n]

        for email in re.finditer(r"([a-zA-z0-9_-]*\.)*[a-zA-z0-9_-]+@+"
                                 r"[a-zA-z0-9_-]+(\.+[a-zA-z0-9_-]+)*",
                                 row):

            # See whether the address is a part of an existing link.
            # If not, it makes it a link.
            # If the email is at the start, it is not part of a link.
            # If the character before the email is : and the character after
            # it is ", it is part of a link.
            # If the character before the email is > and a tag after the
            # email is </a>, it is part of a link.
            if (email.start() == 0) or \
                ((row[email.start() - 1] != ":") and
                 (row[email.start() - 1] != ">")):
                email_text = email.group(0).lower()
                email_link = '<a href="mailto:%s">%s</a>' \
                             % (email_text, email_text)
                new_row = row[:email.start()] + email_link + row[email.end():]
                rows[n] = new_row
                changed = True

    return rows, changed

# r, c = linkify(["oihoiho", "oi666", "wewefw rtrt.we-ERGEE@hj.f, qerefw",
#                 '<a href="mailto:rtrt.we-ergee@hj.f">rtrt.we-ergee@hj.f</a>',
#                 "wer.we.ery.y.uu.it@EWG.WEG.WEeG.ERT", "iohfwoihwe hh@ uhh"])
# for w in r: print(w)


# ---------------------------------------------------------------------------
def main(filetypes, directories, new_file_prefix="", new_file_suffix=""):
    for directory in directories:
        filenames = file_list(filetypes, directory)

        for filename in filenames:
            rows, message = file_reader(filename)

            if message == "":
                new_rows, changed = linkify(rows)

                if changed:
                    message = file_writer(directory, filename, new_rows,
                                          prefix=new_file_prefix,
                                          suffix=new_file_suffix)

                    if message == "":
                        continue

            print(message)


types = [".html"]
directories = ["."]
new_file_prefix = ""
new_file_suffix = "_"
main(types, directories, new_file_prefix, new_file_prefix)
