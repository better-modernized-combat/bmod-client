# https://docs.gspread.org/en/v5.7.0/oauth2.html#for-bots-using-service-account

from argparse import ArgumentParser
import gspread
from gspread.utils import ExportFormat
import json
import os, shutil
from tqdm.auto import tqdm
import pandas as pd
from typing import List, ContextManager
from collections import OrderedDict
import pathlib

class CSVError(Exception):
    pass

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def create_dirtree_without_files(src, dst):
    src = os.path.abspath(src)
    src_prefix = len(src) + len(os.path.sep)
    os.makedirs(dst)
    for root, dirs, files in os.walk(src):
        for dirname in dirs:

            dirpath = os.path.join(dst, root[src_prefix:], dirname)
            os.mkdir(dirpath)

def download_master_sheet(pp: pathlib.Path, url: str):
    gc = gspread.service_account(pp / "service_account.json") ### TODO
    master_sheet = gc.open_by_url(url)
    export_file = master_sheet.export(format = ExportFormat.EXCEL)
    with open(pp / "csv_dump" / "output.xlsx", "wb") as f:
        f.write(export_file)
  
def sheets_to_csvs(pp, excel_file: pathlib.Path, sheet_names: List = None):
    relevant_sheets = pd.read_excel(excel_file, sheet_name = sheet_names)
    for sheet_name, sheet in tqdm(relevant_sheets.items()):
        sheet.to_csv(pp / "csv_dump" / f"{sheet_name}.csv", index = False)

def get_sheet_tab_names(pp: pathlib.Path):
    ini_list = []
    with open(pp / "sheet_contents.json", "r") as o:
        config_data = json.load(o)
    for file in config_data:
        items = file['sheetContents']
        for item in items:
            ini_list.append(item)
    return ini_list

def write_block(block: pd.Series, block_name: str, cols: List, out: ContextManager):
    
    # Check if block is empty. If empty, skip
    if all(pd.isna(x) or x == "" for x in block.values) or block.empty:
        # print(f"Warning: Ignoring empty {block_name} block intended for {out.name} - should this block be empty? If not, please amend the master sheet.")
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

    # if frame.empty is True:
    #     print(f"Warning: Ignoring empty frame intended for {out.name} - should this frame be empty? If not, please amend the master sheet.")

    for _, row in frame.iterrows():

        # Write all keys, assume there are no other keys to write
        cols = frame.columns
        write_block(block = row, block_name = block_name, cols = cols, out = out)

def csv_to_ini(csv_file: str, ini_out_file: str, block_name: str):

    # Get CSV
    try:
        frame = pd.read_csv(csv_file, sep = ",", encoding = "utf-8", comment = "#")
    except (FileNotFoundError, OSError):
        raise
    except Exception:
        raise CSVError(f"CSV {csv_file} couldn't be read and is probably borked.")
    
    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    frame = frame.loc[:, ~frame.columns.str.contains("^Unnamed")]

    # Assume file exists already, append to file
    with open(ini_out_file, "a", encoding = "utf-8") as out:
        frame_to_ini(frame = frame, block_name = block_name, out = out)

def parse_to_list(listable_string):
    return [item.strip() for item in str(listable_string).split("\n")]

def may_shiparch_perish_under_my_wrathful_gaze(
    ship_csv: str,
    simples_csv: str,
    cgroups_csv: str,
    ini_out_file: str,
):
    # Get CSVs
    try:
        ships = pd.read_csv(ship_csv, sep = ",", encoding = "utf-8", comment = "#")
    except:
        raise CSVError(f"CSV {ship_csv} couldn't be read and is probably borked.")
    try:
        simples = pd.read_csv(simples_csv, sep = ",", encoding = "utf-8", comment = "#")
    except:
        raise CSVError(f"CSV {simples_csv} couldn't be read and is probably borked.")
    try:
        cgroups = pd.read_csv(cgroups_csv, sep = ",", encoding = "utf-8", comment = "#")
    except:
        raise CSVError(f"CSV {cgroups_csv} couldn't be read and is probably borked.")
    
    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    ships = ships.loc[:, ~ships.columns.str.contains("^Unnamed")]
    simples = simples.loc[:, ~simples.columns.str.contains("^Unnamed")]
    cgroups = cgroups.loc[:, ~cgroups.columns.str.contains("^Unnamed")]
    shipcols = [col for col in ships.columns if not col in ["simples", "cgroups"]]

    # Assume file exists already, append to file
    with open(ini_out_file, "a", encoding = "utf-8") as out:

        # Write Simples at the top
        frame_to_ini(
        frame = simples,
        block_name = "[Simple]",
        out = out,
        )

        for _, row in ships.iterrows():

            # Get relevant simples and cblocks
            ship = row[~ships.columns.str.contains("simples|cgroups")]
            ship_name = row["nickname"]
            cgroups_names = parse_to_list(row["cgroups"])
            
            # Make them into tiny frames
            cgroups_of_ship = [
                cgroups[(cgroups["ship"] == ship_name) & (cgroups["obj"] == cgroup_name)]
                 for cgroup_name in cgroups_names
                 ]

            # Write ship block, ignoring simples and cblocks column
            write_block(
                block = ship, 
                block_name = "[Ship]", 
                cols = shipcols, 
                out = out
                )

            # Write cblocks
            for cblock in cgroups_of_ship:
                frame_to_ini(
                    frame = cblock, 
                    block_name = "[CollisionGroup]",
                    out = out
                    )

def init_inis(template: dict):

    autogen_comment = [
        ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
        ";; THIS FILE HAS BEEN AUTOMATICALLY GENERATED. ;;",
        ";;        PLEASE DO NOT EDIT THIS FILE.        ;;",
        ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    ]

    legacy_comment = [
        ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
        ";;  THIS CONTENT IS LEGACY CONTENT AND SHOULD  ;;",
        ";;          BE CONSIDERED DEPRECATED.          ;;",
        ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    ]

    sep = [
        ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
        ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    ]

    ini_files = [
        (template[csv]["ini"], 
         template[csv].get("static_ini_content", []),
         template[csv].get("old_content", None))
         for csv in template
         ]

    for file, *_ in ini_files:
        # Delete files
        if os.path.exists(file):
            os.remove(file)
        # Make folders
        else:
            os.makedirs(pathlib.Path(file).parent, exist_ok = True)
        # Make and write to files
        with open(file, "w+") as out:
            for line in autogen_comment:
                out.write(line+"\n")
            out.write("\n")
    for file, static_ini_content, _ in ini_files:
        # First, make one pass to write static ini content
        with open(file, "a") as out:
            for line in static_ini_content:
                out.write(line.strip()+"\n")
            out.write("\n")
    for file, _, old_content in ini_files:
        # Second, make one pass to write old content from separately kept files (such as vanilla ships)
        if old_content:
            with open(file, "a") as out, open(old_content, "r") as old:
                lines = old.readlines()
                out.write("\n")
                for line in legacy_comment:
                    out.write(line+"\n")
                out.write("\n")
                for line in lines:
                    out.write(line.strip()+"\n")
                out.write("\n")
                for line in sep:
                    out.write(line.strip()+"\n")

def generate_inis(master_sheet: str):

    pp = pathlib.Path(__file__).parent
    os.makedirs(pp / "csv_dump", exist_ok = True)
    sheet_names = get_sheet_tab_names(pp)
    template = OrderedDict(json.load(open(pp / "template.json", "r")))

    if master_sheet.startswith("http"):
        print("Grabbing Master Sheet, please wait ...")
        download_master_sheet(pp, url = master_sheet)
        sheets_to_csvs(
            pp = pp, 
            excel_file = pp / "csv_dump" / "output.xlsx", 
            sheet_names = sheet_names
            )
    else:
        print("Extracting CSVs from master sheet...")
        sheets_to_csvs(
            pp = pp, 
            excel_file = master_sheet,
            sheet_names = sheet_names
            )

    print("Creating inis ...")
    init_inis(template = template)

    print("Populating inis ...")
    for csv in template:
        if csv.endswith(".csv"):
            csv_to_ini(
                csv_file = csv,
                ini_out_file = template[csv]["ini"],
                block_name = template[csv]["block_name"]
                )
        elif csv.endswith("shiparch.ini"):
            may_shiparch_perish_under_my_wrathful_gaze(
                ship_csv = template[csv]["ship_csv"],
                simples_csv = template[csv]["simples_csv"],
                cgroups_csv = template[csv]["cgroups_csv"],
                ini_out_file = template[csv]["ini"],
            )
        else:
            raise NotImplementedError("Stop messing around with the template, please.")

    print("Deleting temporary CSV dump...")
    shutil.rmtree(pp / "csv_dump")
    print("Done.")

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "--master_sheet", 
        dest = "master_sheet",
        help = "Takes a valid online URL or a path on the local machine",
        default = "https://docs.google.com/spreadsheets/d/1Uks5GD61Ikrk8VgWPDexOUCoilhhxQ7RmgnhQk9WXS8/"
        )
    args = parser.parse_args()

    generate_inis(master_sheet = args.master_sheet)