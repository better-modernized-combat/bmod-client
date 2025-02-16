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

import sys
sys.path.append("./")

from defaults import *
from ini_utils import *
from generate_guns import create_guns
from generate_lootprops import generate_lootprops
from generate_shiparch import may_shiparch_perish_under_my_wrathful_gaze
from loot_sheet_to_json import create_loot_tables
from sort_ini import sort_ini

from utils import bcolors, root_copy_path

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
    relevant_sheets = pd.read_excel(excel_file, sheet_name = sheet_names, keep_default_na = False)
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

def init_inis(template: dict):

    ini_files = [
        (
            template[csv].get("ini", None), 
            template[csv].get("static_ini_content", []),
            template[csv].get("old_content", None)
        )
        for csv in template
    ]

    for file, *_ in ini_files:
        # If file is None, its a special template entry, ignore
        if file is None:
            continue
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
        # If file is None, its a special template entry, ignore
        if file is None:
            continue
        # First, make one pass to write static ini content
        with open(file, "a") as out:
            for line in static_ini_content:
                out.write(line.strip()+"\n")
            out.write("\n")
    for file, _, old_content in ini_files:
        # If file is None, its a special template entry, ignore
        if file is None:
            continue
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

def generate_inis(master_sheet: str, weapon_sanity_check: bool, generate_loottables: bool):

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
        
        # Special ini
        if csv == "GUNS":
            create_guns(
                blaster_csv = template[csv]["blasters_in"], 
                blaster_variant_csv = template[csv]["blaster_variants_in"], 
                blaster_scaling_rules_csv = template[csv]["blaster_scalings_in"],
                aux_csv = template[csv]["aux_in"], 
                aux_variant_csv = template[csv]["aux_variants_in"],
                weapon_out = template[csv]["weapon_out"],
                weapon_goods_out = template[csv]["weapon_goods_out"],
                weapon_infocards_out = template[csv]["weapon_infocards_out"],
                weapon_sanity_check = weapon_sanity_check,
            )
            
        # Special ini
        elif csv.endswith("SHIPARCH"):
            may_shiparch_perish_under_my_wrathful_gaze(
                ship_csv = template[csv]["ship_csv"],
                simples_csv = template[csv]["simples_csv"],
                cgroups_csv = template[csv]["cgroups_csv"],
                ini_out_file = template[csv]["ini"],
            )
            
        # Special ini
        elif csv == "LOOT TABLES":
            if generate_loottables is True:
                create_loot_tables(
                    loot_table_csv = template[csv]["loot_tables_csv"],
                    out_json = template[csv]["json"]
                )
            else:
                pass
            
        # All regular inis
        elif csv.endswith(".csv"):
            csv_to_ini(
                csv_file = csv,
                ini_out_file = template[csv]["ini"],
                block_name = template[csv]["block_name"]
                )
            
        # This shouldn't exist
        else:
            raise NotImplementedError("Stop messing around with the template, please.")

    # Generate lootprops once all other inis are generated, as lootprops is based on these inis
    # TODO: When merging, convert file names to OS-agnostic format and delete comment
    generate_lootprops(target_file = f"{root_copy_path}\\mod-assets\\DATA\\MISSIONS\\lootprops.ini", no_drops = False)

    # Human-like sorting for any ini with more than one block type
    no_of_block_types = {}
    
    # Figure out which generated inis have more than one block
    for k, v in template.items():
        if not "ini" in v:
            continue
        if v["ini"] in no_of_block_types:
            if "block_name" in v:
                no_of_block_types[v["ini"]].append(v["block_name"])
        else:
            no_of_block_types[v["ini"]] = []
            if "block_name" in v:
                no_of_block_types[v["ini"]].append(v["block_name"])
            
    # For any such generated ini, sort it
    for ini, block_names in no_of_block_types.items():
        if len(set(block_names)) > 1:
            print(f"Sorting {ini} ...")
            #print(f"sort order is: {[x for x in {k: None for k in block_names[::-1]}]}")
            sort_ini(in_file = ini, out_file = ini, order_by_type = [x for x in {k: None for k in block_names[::-1]}]) # that ugly comprehension is an ordered set
            
    # Some special generated inis don't specify block names - sort these as well
    guns = "./mod-assets/DATA/BMOD/EQUIPMENT/bmod_equip_guns.ini"
    print(f"Sorting {guns} ...")
    sort_ini(in_file = guns, out_file = guns, order_by_type = ["[Gun]", "[Munition]"])

    print("Deleting temporary CSV dump...")
    shutil.rmtree(pp / "csv_dump")
    print("Done.")

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "--master_sheet", 
        dest = "master_sheet",
        help = "Takes a valid online URL or a path on the local machine.",
        default = "https://docs.google.com/spreadsheets/d/1Uks5GD61Ikrk8VgWPDexOUCoilhhxQ7RmgnhQk9WXS8/"
        )
    parser.add_argument(
        "--weapon_sanity_check",
        dest = "weapon_sanity_check",
        help = "Whether to run a weapon sanity check that tests for hard imbalances in weapons.",
        default = False,
        action = "store_true"
    )
    parser.add_argument(
        "--generate_loottables",
        dest = "generate_loottables",
        help = "Whether to generate loottables from the sheet, potentially overwriting existing loottables.",
        default = False,
        action = "store_true"
    )
    args = parser.parse_args()

    generate_inis(
        master_sheet = args.master_sheet, 
        weapon_sanity_check = args.weapon_sanity_check, 
        generate_loottables = args.generate_loottables
        )