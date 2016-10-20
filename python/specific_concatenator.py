def main(filename):
    new_filename = "k_" + filename
    opnumlist = []

    with open(filename, 'r', encoding="utf8") as filename:

        for line in filename:
            if line[-1:] == "\n":
                line = line[:-1]
            opnumlist.append(line)

        new_file = ""
        cmd_path1 = ""
        cmd_path2 = ""
        cmd_path3 = ""
        cmd_copy = ""
        cmd_chgrp = ""
        cmd_chmod = ""
        cmd_emacs = ""

        for opnum in opnumlist:
            new_file += cmd_copy + cmd_path1 + opnum + cmd_path2
            new_file += cmd_chgrp + cmd_path1 + opnum + cmd_path2
            new_file += cmd_chmod + cmd_path1 + opnum + cmd_path2
            new_file += cmd_emacs + cmd_path1 + opnum + cmd_path2
            new_file += cmd_emacs + cmd_path1 + opnum + cmd_path3
            new_file += "\n"

        with open(new_filename, 'w+', encoding="utf8") as new_filename:
            new_filename.write(new_file)


main("opnum.txt",)
