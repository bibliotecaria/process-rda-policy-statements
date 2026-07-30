# processes csv file of DITA updates for RDA policy statements
# Columns looked at are: In X update, Current policy, Revised policy for update, Paragraph, DITA key, filename, ID, divID
# Columns output are: New, Revised policy for update, Revised markup, Paragraph, filename, xrefID, divID 
# Spreadsheet preparation includes: copying all formulas at least to divID column

import csv
import os
import re
import argparse
import sys

update_rows = []
spurned_rows = []
boilerplate = {}
keyslist = []
chapter = ""
keynames = ["New", "Revised policy for update", "Revised markup", "Paragraph", "filename", "xrefID", "divID"]
checknames = keynames.copy()
checknames.append("DITA key")
checknames.append("reason")
# add check for blank fields
domain = ""

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

def create_markup_row(current, revised, paragraph, ditakey, filename, xrefid, divID):
    #creates row of revised markup for policy statements with all relevanti information and spurned_row for policy statements that are missing information
    global update_rows
    global spurned_rows
    global domain
    global chapter
    row = {}
    if re.match("new",current,re.IGNORECASE):
        row['New'] = True
    else:
        row['New'] = False
    spurned = False
    spurned_msg = ""
    if revised == "":
        spurned = True
        spurned_msg = "Revised "
    if domain == "":
        spurned = True
        spurned_msg += "Domain "
    row['Revised policy for update'] = revised
    row['Revised markup'] = manipulate_string(revised)
    if paragraph == "":
        spurned = True
        spurned_msg += "Paragraph " 
    row['Paragraph'] = paragraph
    if filename == "":
        spurned = True
        spurned_msg += "Filename " 
    row['filename'] = chapter + "/" + domain + "/" + filename
    row['xrefID'] = ditakey + "/" + xrefid
    # ToDo add guidance and entity type to xrefid
    if row['xrefID'].startswith("/") or row['xrefID'].endswith("/"):
        spurned = True
        spurned_msg += "xrefID " 
    divID = divID.strip()
    row['divID'] = divID
    if " " in divID or divID == "":
        spurned = True
        spurned_msg += "divID " 
    if spurned:
        row["reason"] = spurned_msg
        spurned_rows.append(row)
    else:
        update_rows.append(row)

def write_out(output_file, spurned_file):
    try:
        with open(output_file, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.DictWriter(myfile, fieldnames=keynames)
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
        sys.exit(f"Problem found in writing to {myfile}: {e.__class__.__doc__} [{e.__class__.__name__}]")
    try:
        with open(spurned_file, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.DictWriter(myfile, fieldnames=checknames)
            wr.writeheader()
            for row in spurned_rows:
                hitcounter = hitcounter + 1
                try:
                    if row is not None:
                        wr.writerow(row)
                except Exception as e:
                    sys.exit(f"Problem writing row '{row}' {e.__class__.__doc__} ")
    except Exception as e:
        sys.exit(f"Problem found in writing to {myfile}: {e.__class__.__doc__} [{e.__class__.__name__}]")
    return(hitcounter)
#outputs boilerplate markup or rows that had problems and did not appear with markup

def read_ref_table(reference_file):
    """ 
    Reference file contains policy statements matched to DITA markup.
    It has two columns: "Original text" contains policy statement and "Symbol" contains corresponding DITA markup. 
    """
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

def handle_domain(domstr):
    global domain
    domain = domstr.title()
    domain = domain.replace(" ", "_")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("filename", help="Path to DITA updates csv file required.")
    parser.add_argument("-o", help="Path to output csv file required.")
    parser.add_argument("-s", help="Path to spurned updates csv file required.")
    parser.add_argument("-r", help="Path to reference file of boilerplate conversions.")
    parser.add_argument("-d", help="Optional: Enter chapter type: 'e' for Entity Chapters or 'g' for Guidance Chapters; default is 'e' for Entity Chapters.")
    args = parser.parse_args()
    # validate two arguments
    input_filename = args.filename
    output_file = args.o
    spurned_file = args.s
    reference_file = args.r
    chapter = "Guidance Chapters" if args.d == "g" else "Entity Chapters"
    read_ref_table(reference_file)
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