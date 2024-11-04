from defaults import autogen_comment
from ini_utils import coerce_str_to_bool
from sort_ini import parse_blocks
from tqdm.auto import tqdm

file_map = {
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_amssle.ini": ["[Munition]", "[Gun]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_commodities.ini": ["[Commodity]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_gear.ini": [
        "[CounterMeasure]", 
        "[CounterMeasureDropper]", 
        #"[LootCrate]", 
        "[Mine]", 
        "[MineDropper]", 
        "[Munition]", 
        "[Gun]", 
        "[Thruster]"
        ],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_guns.ini": ["[Munition]", "[Gun]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_npc_only.ini": ["[Munition]", "[Gun]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_playground.ini": [
        "[CounterMeasure]", 
        "[CounterMeasureDropper]", 
        #"[LootCrate]", 
        "[Mine]", 
        "[MineDropper]", 
        "[Munition]", 
        "[Gun]", 
        "[Thruster]", 
        "[ShieldGenerator]"
        ],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_shield.ini": ["[ShieldGenerator]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_solar.ini": ["[Munition]", "[Gun]"],
}                                                           # parse only these files
always_drop = ["bm_com_dev", "voucher", "dogtags"]          # gets 100% drop chance
never_drop = ["_npc"]                                       # gets 0% drop chance, but still has a lootprops entry
never_drop_files = [
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_npc_only.ini",
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_equip_solar.ini"
]                                                           # gets 0% drop chance for all in file, but still has lootprops entries
invalid_blocks = ["[Explosion]", "[LootCrate]", "[Motor]"]  # gets no entry

def block_get(block: dict, keyword: str, default: bool = True):
    
    # Search block content for keyword as if it was a dictionary, run .get with default, return
    d = {line.split("=")[0].strip(): line.split("=")[1].strip() for line in block["content"]}
    return d.get(keyword, default)

def default_properties(block):
    
    # Default per item type
    types = {
        "[Commodity]": "75, 0, 1, 0, 2, 1",
        "[Countermeasure]": "5, 0, 1, 0, 2, 1",
        "[CountermeasureDropper]": "5, 0, 1, 0, 2, 1",
        "[Gun]": "0, 0, 1, 0, 2, 1",
        "[Mine]": "5, 0, 1, 0, 2, 1",
        "[MineDropper]": "5, 0, 1, 0, 2, 1",
        "[Munition]": "5, 0, 1, 0, 2, 1",
        "[ShieldGenerator]": "10, 0, 1, 0, 2, 1",
        "[Thruster]": "5, 0, 1, 0, 2, 1",
    }
    
    # Item should never be dropped
    if any([x in block["nickname"] for x in never_drop]):
        return "0, 0, 1, 0, 2, 1"
    
    # Item should always be dropped
    if any([x in block["nickname"] for x in always_drop]):
        return "100, 0, 1, 0, 2, 1"
    
    # Return default value, or zero if the block type does not have a configured default
    return types.get(block["type"], "0, 0, 1, 0, 2, 1")

def get_drop_properties(block, no_drop: bool = False):
    
    # No drops allowed (for plugin)?
    if no_drop is True:
        drop_properties = "0, 0, 1, 0, 2, 1"
        return drop_properties
    
    # No drops allowed for file?
    if block["file"] in never_drop_files:
        return "0, 0, 1, 0, 2, 1"
    
    # Item should be dropped at the specified rate, defaulting to 0 if empty, missing, or malformed
    drop_properties = block_get(block, keyword = "drop_properties", default = default_properties(block)) # maybe missing
    
    # Empty, 0% drop
    if len(drop_properties) == 0 or drop_properties in ["nan", "", None]: # empty
        return "0, 0, 1, 0, 2, 1"
    
    # Malformed, 0% drop, warning
    if len([n.strip() for n in drop_properties.split(",")]) != 6: # malformed
        print(f"WARNING: Dropping malformed drop_properties entry '{drop_properties}' of {block['nickname']} and defaulting to '0, 0, 1, 0, 2, 1'.")
        return "0, 0, 1, 0, 2, 1"
    
    # Invalid drop chance, 0% drop, warning
    if int(drop_properties.split(",")[0].strip()) < 0 or int(drop_properties.split(",")[0].strip()) > 100:
        print(f"WARNING: Dropping malformed drop_properties entry '{drop_properties}' of {block['nickname']} and defaulting to '0, 0, 1, 0, 2, 1'.")
        return "0, 0, 1, 0, 2, 1"
    
    return drop_properties

def parse_all_files():
    
    all_blocks = []
    
    for file, correct_types in tqdm(file_map.items()):
        
        # parse out all blocks
        start_lines, lines, blocks, nicknames = parse_blocks(file)
        blocks = [block for b, block in blocks.items()]
        for block in blocks:
            block["file"] = file
        
        # toss block types which should never drop
        blocks = [block for block in blocks if not block["type"] in invalid_blocks]
        
        # warn if the block type is false
        false_types = set([block["type"] for block in blocks if not block["type"] in correct_types])
        if len(false_types) >= 1:
            print(f"WARNING: Wrong block type(s) {list(false_types)} in file {file}. Maybe check if you put a new thing into the wrong equipment file (e.g. Shields into the Guns file)? This will not cause a crash.")
        
        # if its a Munition/Mine/CM, it should require_ammo - if not, it should be lootable - else discard
        blocks = [
            block for block in blocks if (
            block["type"] in ["[CounterMeasure]", "[Mine]", "[Munition]"] and coerce_str_to_bool(block_get(block, keyword = "requires_ammo", default = True)) is True
            ) or (
            block["type"] not in ["[CounterMeasure]", "[Mine]", "[Munition]"] and coerce_str_to_bool(block_get(block, keyword = "lootable", default = True)) is True
            )]
        
        all_blocks.extend(blocks)
        
    return all_blocks
        
def generate_lootprops(target_file: str = "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\MISSIONS\\lootprops_gen.ini", no_drops: bool = False):
    
    print("Generating lootprops from configurated files ...")
    all_blocks = parse_all_files()
    with open(target_file, "w") as o:
        for line in autogen_comment:
            o.write(f"{line}\n")
        o.write("\n")
        for block in all_blocks:
            o.write(f"\n\n[mLootProps]\nnickname = {block['nickname']}\ndrop_properties = {get_drop_properties(block, no_drops)}\n")

if __name__ == "__main__":
    
    # TODO: When merging, convert file names to OS-agnostic format and delete comment
    generate_lootprops(target_file = "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\MISSIONS\\lootprops_gen.ini")