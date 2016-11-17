# Matches "__" * ".jpg" and makes assumptions about the length of the filename:
# Renames “__2016-07-24 18.20.27.jpg” to “20160724_182027.png”.

import os


def main(directory="."):
    for filename in os.listdir(directory):
        if filename[:2] == "__" and filename[-4:] == ".jpg":
            d_year = filename[2:6]
            d_month = filename[7:9]
            d_day = filename[10:12]
            d_hour = filename[13:15]
            d_minute = filename[16:18]
            d_second = filename[19:21]
            new_filename = "{0}{1}{2}_{3}{4}{5}.png".format(
                d_year, d_month, d_day, d_hour, d_minute, d_second)
            #print(new_filename)
            os.rename(filename, new_filename)


main()