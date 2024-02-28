from collections import OrderedDict
import os
from pathlib import Path
import re
from tqdm.auto import tqdm
from typing import Callable, List, Union

from replace_gear import recursive_find
from utils import bcolors

# TODO: Fill me, maybe?
excepted_inis = [
    #"bmod_interface_sounds.ini",
    #"bmod_good_guns.ini"
]

# TODO: Fill me with all the hardcoded inis from https://the-starport.com/wiki/ini-editing/
hardcoded_paths = {
    "universe.ini": "UNIVERSE",
}


def parse_ini_to_blocks(lines: List[str, ], block_name: str):
    
    block_starts = []
    block_ends = []
    for n, line in enumerate(lines):
        # If block_name is "[]", any block is checked. Otherwise, specifically block_name blocks are returned
        condition = ((line.lstrip().startswith("[") and line.rstrip().endswith("]")) if block_name == "[]" else (line.strip().lower() == block_name.lower()))
        if condition:
            block_starts.append(n)
    for x in range(len(block_starts) - 1):
        block_ends.append(block_starts[x+1] - 1)
    block_ends.append(len(lines) - 1)
    
    return block_starts, block_ends


def validate_entries(source_ini: str, source_block: str, source_key: str, target_ini: Union[List[str, ], str], target_block: str, target_key: str, blocking: bool):
    
    """
    For every block of type source_block in source_ini, look for source_key and save the value with its line in a dict.
    Go thorugh every target_block in every target_ini and check if target_key is one of the referenced values from before.
    If so, remove that value from the dict.
    Any remaining values are invalid and an error (blocking is True) or a warning (blocking is False) is raised.
    """
    
    with open(source_ini, "r") as f:
        source_lines = f.readlines()
    if isinstance(target_ini, str):
        target_inis = [target_ini]
    else:
        target_inis = target_ini
    target_lines = {}
    for ini in target_inis:
        with open(ini, "r") as f:
            lines = f.readlines()
        target_lines[ini] = lines
    
    source_block_starts, source_block_ends = parse_ini_to_blocks(source_lines, source_block)
    referenced_objects = OrderedDict()
    
    # Iterate over all blocks in the source_ini
    for bs, be in zip(source_block_starts, source_block_ends):
        # Iterate over all lines in a block
        for n, line in enumerate(source_lines[bs:be+1]):
            # Line can't contain the source key + referenced object
            if not "=" in line:
                continue
            # Line could contain the source key + referenced object
            split = line.split("=")
            if not split[0].strip() == source_key:
                continue
            # Line has source key + referenced object, save them with their line number
            # If there are several references in one line, split by comma and strip any spaces
            refs_found = [ref.strip() for ref in split[1].split(",")]
            for ref in refs_found:
                # Ints and Floats sometimes crop up as part of a line, but they can't be object nicknames, or so I sincerely hope
                if all([s.isdigit() or s == "." or s == "-" for s in ref]):
                    continue
                elif not ref in referenced_objects:
                    referenced_objects[ref] = [n+bs]
                else:
                    referenced_objects[ref].append(n+bs)
    no_of_referenced_objects = len(referenced_objects)
    
    # Iterate over all target_inis
    for ini in target_inis:
        # Parse the blocks out of the target_ini
        target_block_starts, target_block_ends = parse_ini_to_blocks(target_lines[ini], target_block)
        # Iterate over all blocks in the target_ini
        for bs, be in zip(target_block_starts, target_block_ends):
            # Iterate over all lines in a block
            for n, line in enumerate(target_lines[ini][bs:be+1]):
                # Line can't contain the target key
                if not "=" in line:
                    continue
                # Line could contain the target key
                split = line.split("=")
                if not split[0].strip() == target_key:
                    continue
                # Line has target key (implicit assumption: Line has only 1 value)
                # Find all references that are proven valid by this line
                found = []
                for ref in list(referenced_objects.keys()):
                    if split[1].strip() == ref:
                        found.append(ref)
                for ref in found:
                    del referenced_objects[ref]
    # Any remaining ref in referenced_objects is invalid, report the respective lines
    if len(referenced_objects) == 0:
        print(f"{bcolors.OKGREEN}✓ All {source_block}->{source_key} references for {source_ini} appear valid (checked {no_of_referenced_objects} references against {target_ini}).{bcolors.ENDC}")
    else:
        for ref, line_nos in referenced_objects.items():
            print(f"{bcolors.WARNING}Found invalid reference to {ref} in line(s) {line_nos} in {source_ini}.{bcolors.ENDC}")
        if blocking is True:
            print(f"{bcolors.FAIL}Found {len(referenced_objects)} invalid {source_block}->{source_key} object references for {source_ini}.{bcolors.ENDC}")
            raise INIError
        else:
            print(f"{bcolors.WARNING}Found {len(referenced_objects)} invalid {source_block}->{source_key} object references for {source_ini}.{bcolors.ENDC}")


def get_hcp(long_ini: str):
    
    hcp = hardcoded_paths.get(long_ini, "")
    # Direct hit, captain, full path found
    if hcp != "":
        return hcp
    # Maybe its just the file without the path
    else:
        for short_ini in hardcoded_paths:
            if long_ini.endswith(short_ini):
                return hardcoded_paths[short_ini]
        # Don't have it
        return ""


class INIError(Exception):
    pass


def validate_ammo(mod_build_dir: str, blocking: bool = False):
    # Any referenced ammunition points to a valid ammunition block.
    validate_entries(
        source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", "bmod_equip_guns.ini"),
        source_block = "[Gun]",
        source_key = "projectile_archetype",
        target_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", "bmod_equip_guns.ini"), 
        target_block = "[Munition]",
        target_key = "nickname",
        blocking = blocking
        )
    validate_entries(
        source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", "bmod_equip_amssle.ini"),
        source_block = "[Gun]",
        source_key = "projectile_archetype",
        target_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", "bmod_equip_amssle.ini"), 
        target_block = "[Munition]",
        target_key = "nickname",
        blocking = blocking
        )


def validate_encounters(mod_build_dir: str, blocking: bool = False):
    # Get system ini files for all systems:
    system_inis = [file for file in recursive_find(os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "UNIVERSE", "SYSTEMS")) if not "base" in file]
    encounter_inis = [file for file in recursive_find(os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "ENCOUNTERS")) if not "base" in file]
    target_lines = {"<improvised ini - not a file>": ["[]\n"]+[f"nickname = {encounter.replace('.ini', '')}" for encounter in encounter_inis]}
    
    # For all system inis:
    for system_ini in system_inis:
        # Encounters in [Zone] blocks correctly reference an [EncounterParameters] block.
        validate_entries(
            source_ini = system_ini,
            source_block = "[Zone]",
            source_key = "encounter",
            target_ini = system_ini,
            target_block = "[EncounterParameters]",
            target_key = "nickname",
            blocking = blocking
            )


def validate_faction_prop(mod_build_dir: str, blocking: bool = False):
    # npcships defined in faction_prop.ini point to a valid npcship in npcships.ini.
    validate_entries(
        source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "MISSIONS", "faction_prop.ini"),
        source_block = "[FactionProps]",
        source_key = "npc_ship",
        target_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "MISSIONS", "npcships.ini"),
        target_block = "[NPCShipArch]",
        target_key = "nickname",
        blocking = blocking
        )


def validate_file_paths(mod_build_dir: str, actively_fix_casing: bool = False, blocking: bool = False):
    
    mod_data_dir = os.path.join(os.path.abspath(mod_build_dir), "mod-assets", "DATA")
    vanilla_data_dir = os.path.join(os.environ["FL_PATH"].replace("\\EXE", "\\DATA").replace("/EXE", "/DATA"))
    inis = recursive_find(os.path.abspath(mod_build_dir))
    no_of_matches = 0
    no_of_problems = 0
    no_of_files_w_problems = 0
    fixed_casings = 0
    
    for ini in tqdm(inis):
        
        # Skip specific ini files
        if any([ini.endswith(x) for x in excepted_inis]):
            continue
        
        no_of_local_problems = 0
        lines = open(ini, "r").readlines()
        new_lines = []
        
        for n, line in enumerate(lines):
            
            # Skip lines with comments
            if line.lstrip().startswith(";"):
                new_lines.append(line)
                continue
            
            # File references ok?
            matches = re.findall(r'([^,\s]*?\\+[^,\s]+)', line)
            #if matches:
            #    print(matches)
            #    break
            if matches:
                no_of_matches += 1
                for match in matches:
                    vp = get_hcp(ini)
                    # Path is complete except for vanilla_Data_dir
                    if match.startswith(vp):
                        vanilla_path = os.path.join(vanilla_data_dir, match)
                    else:
                        vanilla_path = os.path.join(vanilla_data_dir, get_hcp(ini), match)
                    mp = get_hcp(ini)
                    # Path is complete except for mod_data_dir
                    if match.startswith(mp):
                        mod_path = os.path.join(mod_data_dir, match)
                    # Path is incomplete at the start
                    else:
                        mod_path = os.path.join(mod_data_dir, get_hcp(ini), match)
                    bmp = os.path.join("BMOD", get_hcp(ini))
                    # Path is complete except for mod_data_dir\BMOD
                    if match.startswith(bmp):
                        bmod_path = os.path.join(mod_data_dir, match)
                    # Path is partially incomplete at the start (e.g. has UNIVERSE but not BMOD/UNIVERSE)
                    elif match.startswith(mp):
                        bmod_path = os.path.join(mod_data_dir, "BMOD", match)
                    # Path is incomplete at the start
                    else:
                        bmod_path = os.path.join(mod_data_dir, bmp, match)
                    
                    # Path may be valid only with Windows-specific case-insensitivity, try resolving
                    if actively_fix_casing is True:
                        
                        res_vanilla_path = Path(vanilla_path).resolve(strict = False)
                        res_mod_path = Path(mod_path).resolve(strict = False)
                        res_bmod_path = Path(bmod_path).resolve(strict = False)
                        
                        if str(res_vanilla_path) != str(vanilla_path) or str(res_mod_path) != str(mod_path) or str(res_bmod_path) != str(bmod_path):
                            must_fix_path = True
                            #print(f"INFO: {ini} references {match} in line {n}, which resolves to a valid path only with resolved casing. Fixing ...")
                        else:
                            must_fix_path = False
                    else:
                        must_fix_path = False
                    
                    # Try the path
                    if (os.path.isfile(vanilla_path) or os.path.isdir(vanilla_path) or os.path.isfile(mod_path) or os.path.isdir(mod_path) or os.path.isfile(bmod_path) or os.path.isdir(bmod_path)):
                        # Fix paths by replacing our match with the correctly cased version provided by path resolve (get cut by splitting around the match, giving the path we dont need and "")
                        if must_fix_path is True:
                            if (os.path.isfile(vanilla_path) or os.path.isdir(vanilla_path)):
                                cut = [x for x in str(vanilla_path).split(match) if x != ""][0]
                                fixed = str(res_vanilla_path).replace(cut, "")
                            elif os.path.isfile(mod_path) or os.path.isdir(mod_path):
                                cut = [x for x in str(mod_path).split(match) if x != ""][0]
                                fixed = str(res_mod_path).replace(cut, "")
                            else:
                                cut = [x for x in str(bmod_path).split(match) if x != ""][0]
                                fixed = str(res_bmod_path).replace(cut, "")
                            line = line.replace(match, fixed)
                            fixed_casings += 1
                        continue
                    # Path is definitely invalid
                    else:
                        no_of_local_problems += 1
                        no_of_problems += 1
                        #print(vanilla_path)
                        #print(mod_path)
                        #print(bmod_path)
                        #print(res_vanilla_path)
                        #print(res_mod_path)
                        #print(res_bmod_path)
                        print(f"{bcolors.WARNING}WARNING: {ini} references {match} in line {n}, which does not seem to resolve to a valid path.{bcolors.ENDC}")
                # After going over all matches add the line back for potential overwriting
                new_lines.append(line)
            # no matches
            else:
                new_lines.append(line)
        
        if no_of_local_problems > 0:
            no_of_files_w_problems += 1
        #    raise INIError(f"DEBUG: Invalid path(s) found in {ini}, stopping.")
        
        # Fix casing, but only if no other problems are present (else we might mangle bad file paths beyond recognition and erase hours of work).
        # Let the user fix their paths first, the we'll worry about casing.
        if actively_fix_casing is True and no_of_problems == 0:
            with open(ini, "w") as out:
                for line in new_lines:
                    out.write(line)
    
    # Fixed casing?
    if actively_fix_casing is True:
        if no_of_problems == 0 and fixed_casings > 0:
            print(f"{bcolors.WARNING}WARNING: Fixed {fixed_casings}/{no_of_matches} paths with incorrect casing. << Bap >>{bcolors.ENDC}")
        elif fixed_casings > 0:
            print(f"{bcolors.WARNING}WARNING: There are {fixed_casings}/{no_of_matches} paths with incorrect casing that want to be fixed. << Bap >>{bcolors.ENDC}")
        else:
            pass
    # Found no problems            
    if no_of_problems == 0:
        print(f"{bcolors.OKGREEN}✓ All INI file path references are valid (checked {no_of_matches} paths in {len(inis)} files).{bcolors.ENDC}")
    # Found problems
    else:
        # Do it again chief
        if blocking:
            print(f"{bcolors.FAIL}ERROR: Found {no_of_problems}/{no_of_matches} invalid paths (see above) in {no_of_files_w_problems} separate file(s).{bcolors.ENDC}")
            raise INIError
        # Who cares
        else:
            print(f"{bcolors.WARNING}WARNING: Found {no_of_problems}/{no_of_matches} invalid paths (see above) in {no_of_files_w_problems} separate file(s).{bcolors.ENDC}")
    print(no_of_matches)


def validate_goods(mod_build_dir: str, blocking: bool = False):
    # Any equipment referenced by a good points to an existing piece of equipment.
    goods_files = {
        "amssle":       ["[]", "nickname"],
        "commodities":  ["[Commodity]", "nickname"],
        "gear":         ["[]", "nickname"],
        "guns":         ["[]", "nickname"],
        "npc_only":     ["[]", "nickname"],
        "playground":   ["[]", "nickname"],
        "shield":       ["[ShieldGenerator]", "nickname"],
    }
    for name, (tb, tk) in goods_files.items():
        validate_entries(
            source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", f"bmod_good_{name}.ini"),
            source_block = "[Good]",
            source_key = "equipment",
            target_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", f"bmod_equip_{name}.ini"),
            target_block = tb,
            target_key = tk,
            blocking = blocking
            )


def validate_market_goods(mod_build_dir: str, blocking: bool = False):
    # Any good referenced in market goods points to a valid good block.
    
    # Commodities
    validate_entries(
        source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", f"bmod_market_commodities.ini"),
        source_block = "[BaseGood]",
        source_key = "MarketGood",
        target_ini = [
            os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", f"bmod_good_commodities.ini"),
            os.path.join((os.environ["FL_PATH"].replace("\\EXE", "\\DATA").replace("/EXE", "/DATA")), "EQUIPMENT", "goods.ini")
            ],
        target_block = "[Good]",
        target_key = "nickname",
        blocking = blocking
    )
    # Any other goods
    other_goods_inis = [f"bmod_good_{name}.ini" for name in ["amssle", "guns", "gear", "npc_only", "playground", "shield"]]
    validate_entries(
        source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", f"bmod_market_misc.ini"),
        source_block = "[BaseGood]",
        source_key = "MarketGood",
        target_ini = [os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "EQUIPMENT", ini) for ini in other_goods_inis],
        target_block = "[Good]",
        target_key = "nickname",
        blocking = blocking
    )


def validate_npcships(mod_build_dir: str, blocking: bool = False):
    # Loadouts in npcships.ini point to a valid loadout.
    validate_entries(
        source_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "MISSIONS", "npcships.ini"),
        source_block = "[NPCShipArch]",
        source_key = "loadout",
        target_ini = os.path.join(mod_build_dir, "mod-assets", "DATA", "BMOD", "SHIPS", "bmod_loadouts_npc.ini"),
        target_block = "[Loadout]",
        target_key = "nickname",
        blocking = blocking
        )


if __name__ == "__main__":

    mod_build_dir = os.path.abspath("./")
    print("Validating INI files ...")
    validate_file_paths(mod_build_dir = "./", actively_fix_casing = True, blocking = True)
    validate_ammo(mod_build_dir, blocking = True)
    validate_encounters(mod_build_dir, blocking = True)
    validate_faction_prop(mod_build_dir, blocking = True)
    validate_goods(mod_build_dir, blocking = True)
    validate_market_goods(mod_build_dir, blocking = True)
    validate_npcships(mod_build_dir, blocking = True)