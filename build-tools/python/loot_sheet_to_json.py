import json
import os
import pandas as pd
import pathlib
from typing import List
from ini_utils import clean_unnamed_wip_empty

def compress_frame(csv: pd.DataFrame) -> pd.DataFrame:
    
    compressible = ["item", "dropCounts", "weighting"]
    compressed = {col: {} for col in compressible}
    
    # collect compressible items
    for index, row in csv.iterrows():
        
        if not (pd.isna(row["nickname"]) or row["nickname"] == ""):
            current_index = int(index)
            continue
        
        for col in compressible:
            if not current_index in compressed[col]:
                compressed[col][current_index] = [str(row[col]).strip(",").split(",")]
            else:
                compressed[col][current_index].append(str(row[col]).strip(",").split(","))
    
    # compress and replace rows
    for col in compressible:
        csv[col] = [compressed[col].get(i, "") for i in range(len(csv))]
    
    return csv

def convert_to_nested_lists(string: str) -> List:

    nested_list = [substring.strip(",").split(",") for substring in string.strip().split("\n")]
    
    return nested_list

def convert_to_json_format(csv: pd.DataFrame) -> dict:
    
    j = {
        "lootDropContainer": "lootcrate_ast_loot_metal", 
        "lootTables": []
        }
    
    for _, row in csv.iterrows():
            
        table = {col: row[col] for col in ["applyToNpcs", "applyToPlayers", "nickname", "triggerItem"]}
        table.update({
            "rollCount": int(float((row["rollCount"]))),
            "dropWeights": [
                    {
                        "item": item[0],
                        "dropCounts": [int(float(c)) for c in dropCounts], # Dont ask about int(float(c)) please
                        "weighting": int(float(weighting[0])) # TODO: Can we abandon ints here please? This needs to be done on the plugin side
                    }
                    for item, dropCounts, weighting in zip(row["item"], row["dropCounts"], row["weighting"])
                ]
            })
        j["lootTables"].append(table)
    
    return j

def create_loot_tables(loot_table_csv: str, out_json: str):
    
    out_json = pathlib.Path(out_json)
    
    csv = pd.read_csv(loot_table_csv)
    csv = compress_frame(csv)
    csv = clean_unnamed_wip_empty(csv, loot_table_csv)
    j = convert_to_json_format(csv)
    os.makedirs(out_json.parent, exist_ok = True)
    with open(out_json, "w") as o:
        o.write(json.dumps(j, indent = 2))