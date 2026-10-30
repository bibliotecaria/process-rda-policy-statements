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
import datetime
import xml.etree.ElementTree as ET

logs = []
update_list = {}

def print_logline(line):
    return(f"{line["time"]}\t{line["status"]}\t{line["statement"]}\t{line["filename"]}\t{line["divID"]}\t{line["error"]}")

def write_log(log):
    try:
        with open(log, "w", newline='', encoding='utf-8') as myfile:
            for line in logs:
                myfile.write(print_logline(line))
    except Exception as e:
        sys.exit((f"Problem found in writing to {myfile}: {e.__class__.__doc__} [{e.__class__.__name__}]"))

def logline(status, statement, filename = "", divID = "", error = ""):
    t = datetime.datetime.now()
    tstring = t.strftime("%Y-%m-%d %H:%M:%S")
    line = {
        "time" : tstring,
        "status" : status,
        "statement" : statement,
        "filename" : filename,
        "divID" : divID,
        "error" : error
        }
    logs.append(line)
    return(line)


def get_update_list(input_filename):
    with open(input_filename, newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        for row in reader:
            counter += 1
            if row["filename"] in update_list:
                update_list[row["filename"]].append(row)
            else:
                update_list[row["filename"]] = [row]

# returns True for successful update
def add_para(div, rev_markup, parano, plist):
    pass

# returns True for successful update
def replace_para(div, rev_markup, parano, plist):
    pass

# returns True for successful update
def delete_para(parano, plist):
    p = plist[parano]
    parent= p.getparent()
    parent.remove(p)
    # we need to put this process in a try/catch


# returns True for successful update
def execute_update(div, update_row):
    # get paragraph number from update row in XXupdate.csv
    parano = update_row["Paragraph"]
    parano = int(parano) - 1
    isnew = (update_row["New"] == "True")
    print(update_row)
    # get paragraph list of div in DITA file
    plist = div.findall("p")
    ismismatch = False
    if len(plist) < parano:
        if not isnew:
            ismismatch = True
        elif len(plist) < (parano - 1):
            ismismatch = True
    if ismismatch:
        print_logline(logline("Warning", "Paragraph number mismatch", f"{update_row["filename"]}, {update_row["divID"]}"))
        return(False)
    if update_row["Revised policy for update"] == "DELETE":
        print("DELETE")
    elif isnew:
        print("New")
    else:
        print("modify")

def process_update_list(directory):
    for filename in update_list:
        filepath = directory + "/" + filename
        # filepath = filename
        try:
            tree = ET.parse(filepath)
            topic = tree.getroot()
            #topic is root of DITA file
            for update_row in update_list[filename]:
                path = './/*[@id="'+ update_row["divID"] +'"]'
                div = topic.find(path)
                if div is not None:
                    #decide on what to do with div here: add, replace, or delete
                    execute_update(div, update_row)
                else:
                    print(print_logline(logline("Warning", "Div not found", filepath, f"Element with specified ID [{path}] not found.")))        
        except FileNotFoundError:
            print(print_logline(logline("Failure", "Opened DITA file", filepath, "File not found.")))        
        except ET.ParseError:
            print(print_logline(logline("Failure", "Parsed DITA file", filepath, f"{e.__class__.__doc__} [{e.__class__.__name__}]")))
        except Exception as e:
            err = f"{e.__class__.__doc__} [{e.__class__.__name__}]"
            print(err)


if __name__ == "__main__":
    print(print_logline(logline("Success", "Start process")))
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
        err = "Can't find filename " + input_filename + "; "
    if not os.path.exists(input_directory):
        err += "Can't find input directory " + input_directory + "; "
    try:
        os.makedirs(output_directory, exist_ok=True)
        print(print_logline(logline("Success", "Created output directory", output_directory)))
    except Exception as e:
        err += "Error creating directory " + output_directory + " [" + e + "] "
    if err != "":
        print_logline(logline("Abort", err))
        write_log(log_file)
        sys.exit(f"Aborted for error(s); see log file {log_file}")
    # now we're good!
    get_update_list(input_filename)
    process_update_list(input_directory)
    print("done")

