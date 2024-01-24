from typing import List, ContextManager
import pandas as pd

class CSVError(Exception):
    pass

def parse_to_list(listable_string: str):
    return [item.strip() for item in str(listable_string).split("\n")]

def clean_unnamed_wip_empty(frame: pd.DataFrame, name: str):
    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    frame = frame.loc[:, ~frame.columns.str.contains("^Unnamed")]
    
    # TODO: Clean out rows where WIP? is any kind of true
    # TODO: Clean out the WIP? col, if any
    if "WIP" in frame.columns:
        l0 = len(frame)
        frame = frame[frame["WIP"] != "TRUE"]
        frame = frame.loc[:, ~frame.columns.str.contains("WIP")]
        l1 = len(frame)
        if l1 != l0:
            print(f"DEBUG: Dropped {l0-l1} WIP rows from frame {name}.")
    
    # TODO: Clean out rows where the nickname is missing, as presumably they are unused as of yet
    l0 = len(frame)
    for priv_col in ["nickname", "obj", "Weapon Name"]:
        if priv_col in frame.columns:
            frame = frame.dropna(subset = [priv_col])
    l1 = len(frame)
    if l1 != l0:
        print(f"DEBUG: Dropped {l0-l1} empty rows from frame {name}.")
    
    return frame

def write_block(block: pd.Series, block_name: str, cols: List, out: ContextManager):
    
    # Check if block is empty. If empty, skip
    if all(pd.isna(x) or x == "" for x in block.values) or block.empty:
        print(f"Warning: Ignoring empty {block_name} block intended for {out.name} - should this block be empty? If not, please amend the master sheet.")
        return

    # Write block header
    out.write("\n")
    out.write(block_name+"\n")

    # Write block
    for e, col in enumerate(cols):
        line = str(block.iloc[e]).strip()
        if "\n" in line:
            sublines = line.split("\n")
            for subline in sublines:
                if subline.strip() == "":
                    continue
                out.write(col+" = "+subline+"\n")
        else:
            if line.strip() in ["", "nan"]:
                continue
            out.write(col+" = "+line+"\n")

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