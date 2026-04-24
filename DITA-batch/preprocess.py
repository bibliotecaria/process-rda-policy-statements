# processes csv file of DITA updates for RDA policy statements
# Columns looked at are: In X update, Current policy, Revised policy for update, Paragraph, filename, divID
# Columns output are: New, Revised policy for update, Revised markup, Paragraph, filename, divID 

import csv
import os
import re
import argparse
import sys

update_rows = []
boilerplate = {}
keyslist = []


def sym_subs(string):
    newstring = string
    for key in keyslist:
        inx = newstring.find(key)
        if inx > -1:
            newstring = newstring.replace(key,boilerplate[key])
    return(newstring)
            # do the replacement from boilerplate[key]

def manipulate_string(string):
    while True:
        newstring = sym_subs(string)
        if newstring == string:
            break
        string = newstring
    return(string)

def create_markup_row(current, revised, paragraph, filename, divID):
    global update_rows
    row = {}
    if re.match("new",current,re.IGNORECASE):
        row['New'] = True
    else:
        row['New'] = False
    row['Revised policy for update'] = revised
    row['Revised markup'] = manipulate_string(revised)
    row['Paragraph'] = paragraph
    row['filename'] = filename
    row['divID'] = divID
    update_rows.append(row)

def write_out(output_file):
    fieldnames =["New", "Revised policy for update", "Revised markup", "Paragraph", "filename", "divID"]
    try:
        with open(output_file, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.DictWriter(myfile, fieldnames=fieldnames)
            wr.writeheader()
            hitcounter = 0
            for row in update_rows:
                hitcounter = hitcounter + 1
                try:
                    if row is not None:
                        wr.writerow(row)
                except Exception as e:
                    sys.exit(f"Problem writing row '{row}' {e.__class__.__doc__} ")
    except Exception as e:
        sys.exit(f"Problem found in writing to {csvfile}: {e.__class__.__doc__} [{e.__class__.__name__}]")
    return(hitcounter)
#outputs boilerplate markup

def read_ref_table(reference_file):
    # Two columns: "Original text", "Symbol"
    global keyslist
    with open(reference_file, newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        for row in reader:
            text = row["Original text"].strip('"').replace('\xa0', ' ')
            boilerplate[text] = row["Symbol"]
            counter += 1
    keyslist = list(boilerplate.keys())
    keyslist.sort(key=lambda x: len(x))
    keyslist = keyslist[::-1]
    # reads in table, organizes by longest strings first, and turns into a dict
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("filename", help="Path to DITA updates csv file required.")
    parser.add_argument("-o", help="Path to output csv file required.")
    parser.add_argument("-r", help="Path to reference file of boilerplate conversions.")
    args = parser.parse_args()
    # validate two arguments
    input_filename = args.filename
    output_file = args.o
    reference_file = args.r
    read_ref_table(reference_file)


    with open(input_filename, newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        for row in reader:
            counter += 1
            if row['In X update'] != "":
                create_markup_row(row['Current policy'], row['Revised policy for update'], row['Paragraph'], row['filename'], row['divID'])
    counter = write_out(output_file)
    print(f"{counter} records written to {output_file}")