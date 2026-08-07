"""
Program to process preprocessed csv file of updates to DITA files.
Input csv columns: New (T/F), Revised policy for update (plain English), Revised markup, Paragraph (number), filename (subdirectories and filename), xrefID, divID
Output: updated DITA files into new, replicated subdirectory structure, log file
Log file format: csv: Message, all Input columns
"""

import csv
import os.path
import os
import re
import argparse
import sys

logs = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("-old", help="Path to old subdirectory required.")
    parser.add_argument("-new", help="Path to new subdirectory required.")
    parser.add_argument("-update", help="Path to preprocessed updates csv file required.")
    parser.add_argument("-log", help="Path to log csv file required.")
    args = parser.parse_args()
    input_filename = args.update
    output_directory = args.new
    input_directory = args.old
    log_file = args.log
    err = ""
    if not os.path.exists(input_filename):
        err = "Can't find filename " + input_filename + " "
    if not os.path.exists(input_directory):
        err += "Can't find input directory " + input_directory + " "
    try:
        os.makedirs(output_directory, exist_ok=True)
    except Exception as e:
        err += "Error creating directory " + output_directory + " [" + e + "] "
    if err != "":
        sys.exit(f"Unable to continue {err}")
    # now we're good!

    with open(input_filename, newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        for row in reader:
            counter += 1
            if row['In X update'] != "":
                handle_domain(row['Domain'])
                create_markup_row(row['Current policy'], row['Revised policy for update'], row['Paragraph'], row['DITA Key'], row['filename'], row['ID'], row['divID'])
    counter = write_out(output_file, spurned_file)
    print(f"{counter} records written to {output_file} or {spurned_file}")