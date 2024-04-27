import pandas as pd
from ini_utils import CSVError, clean_unnamed_wip_empty, frame_to_ini, parse_to_list, write_block

def may_shiparch_perish_under_my_wrathful_gaze(
    ship_csv: str,
    simples_csv: str,
    cgroups_csv: str,
    ini_out_file: str,
):
    # Get CSVs
    try:
        ships = pd.read_csv(ship_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {ship_csv} couldn't be read and is probably borked.")
    try:
        simples = pd.read_csv(simples_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {simples_csv} couldn't be read and is probably borked.")
    try:
        cgroups = pd.read_csv(cgroups_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {cgroups_csv} couldn't be read and is probably borked.")
    
    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    #ships = ships.loc[:, ~ships.columns.str.contains("^Unnamed")]
    ships = clean_unnamed_wip_empty(ships, name = "shiparch")
    #simples = simples.loc[:, ~simples.columns.str.contains("^Unnamed")]
    simples = clean_unnamed_wip_empty(simples, name = "simples")
    #cgroups = cgroups.loc[:, ~cgroups.columns.str.contains("^Unnamed")]
    cgroups = clean_unnamed_wip_empty(cgroups, name = "cgroups")
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