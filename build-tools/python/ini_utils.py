from typing import List, ContextManager
import pandas as pd

class CSVError(Exception):
    pass

def pretty_numbers(s: str):
    
    # if its not a string, send out the kill squad. also make it a string
    s = str(s)
    
    # if the string can be a number
    if not s.replace(".", "", 1).isdigit() or (s.startswith("-") and s[1:].replace(".", "", 1).isdigit()):
        return s
    
    # is it an int?
    if not "." in s:
        return str(int(s))
    
    # if not, make it a float and round to 4 decimal places, eliminating trailing zeroes or commas
    else:
        s = float(s)
        return f"{round(s, 4):.4f}".rstrip('0').rstrip('.')

def parse_to_list(listable_string: str):
    return [item.strip() for item in str(listable_string).split("\n")]

def clean_unnamed_wip_empty(frame: pd.DataFrame, name: str):
    
    # These column names, if they exist, are used to determine whether rows can be discarded
    privileged_column_names = ["nickname", "obj", "Weapon Name"]
    
    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    frame = frame.loc[:, ~frame.columns.str.contains("^Unnamed")]
    
    # Clean out rows where WIP is any kind of true
    if "WIP" in frame.columns:
        l0 = len(frame)
        frame = frame[frame["WIP"].apply(pd.isna)] # If its empty, its not WIP.
        frame = frame.loc[:, ~frame.columns.str.contains("WIP")]
        l1 = len(frame)
        if l1 != l0:
            print(f"DEBUG: Dropped {l0-l1} WIP rows from frame {name}.")
    
    # Clean out rows where the nickname is missing, as presumably they are unused as of yet
    l0 = len(frame)
    for pcn in privileged_column_names:
        if pcn in frame.columns:
            frame = frame.dropna(subset = [pcn])
            frame = frame[frame[pcn] != ""]
    l1 = len(frame)
    if l1 != l0:
        print(f"DEBUG: Dropped {l0-l1} empty rows from frame {name}.")
    
    return frame

def write_block(block: pd.Series, block_name: str, cols: pd.Index, out: ContextManager):
    
    # Check if block is empty. If empty, skip
    if all(pd.isna(x) or x == "" for x in block.values) or block.empty:
        print(f"Warning: Ignoring empty {block_name} block intended for {out.name} - should this block be empty? If not, please amend the master sheet.")
        return

    if isinstance(cols, pd.Index):
        cols_as_list = cols.to_list()
    else:
        cols_as_list = cols

    # Write block header
    out.write("\n")
    if "Comment" in cols:
        comment = str(block.iloc[cols_as_list.index('Comment')])
        if comment != "nan":
            out.write(f";{comment}\n")
    out.write(block_name+"\n")

    # Write block
    for e, col in enumerate(cols):
        value = str(block.iloc[e]).strip()
        if "\n" in value:
            subvalues = value.split("\n")
            for subvalue in subvalues:
                if subvalue.strip() == "":
                    continue
                out.write(col+" = "+pretty_numbers(subvalue)+"\n")
        else:
            if value.strip() in ["", "nan"] or col == "Comment":
                continue
            out.write(col+" = "+pretty_numbers(value)+"\n")

    out.write("\n") # end of block

def frame_to_ini(frame: pd.DataFrame, block_name: str, out: ContextManager):
    """
    Write all blocks of a type to an already opened file. 
    frame wants to be the pandas DataFrame,
    block_name wants to be the name for the type of block we insert,
    out wants to be the context manager (with open(XYZ) as o:).
    """

    if frame.empty is True:
        print(f"Warning: Ignoring empty frame intended for {out.name} - should this frame be empty? If not, please amend the master sheet.")

    for _, row in frame.iterrows():

        # Write all keys, assume there are no other keys to write
        cols = frame.columns
        write_block(block = row, block_name = block_name, cols = cols, out = out)

def csv_to_ini(csv_file: str, ini_out_file: str, block_name: str):

    # Get CSV
    try:
        frame = pd.read_csv(csv_file, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except (FileNotFoundError, OSError):
        raise
    except Exception:
        raise CSVError(f"CSV {csv_file} couldn't be read and is probably borked.")
    
    frame = clean_unnamed_wip_empty(frame = frame, name = csv_file)

    # Assume file exists already, append to file
    with open(ini_out_file, "a", encoding = "utf-8") as out:
        frame_to_ini(frame = frame, block_name = block_name, out = out)