from defaults import autogen_comment
from ini_utils import coerce_str_to_bool
from sort_ini import parse_blocks
from tqdm.auto import tqdm

# TODO: Weapons/Ammo or Good or both? If only one, remove corresponding drop_properties entries from the other in generate_guns.py
# TODO: Are there other block types Playground should check for?

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
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_amssle.ini": ["[Munition]", "[Gun]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_commodities.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_gear.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_guns.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_npc_only.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_playground.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_good_shield.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_market_commodities.ini": ["[Good]"],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_market_misc.ini": [],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_market_ships.ini": [],
    "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_weaponmoddb.ini": [],
}
always_drop = ["bm_com_dev", "voucher", "dogtags"]
never_drop = ["_npc_"]

def block_get(block: dict, keyword: str, default: bool = True):
    
    # Search block content for keyword as if it was a dictionary, run .get with default, return
    d = {line.split("=")[0].strip(): line.split("=")[1].strip() for line in block["content"]}
    return d.get(keyword, default)

def get_drop_properties(block):
    
    # Item should never be dropped
    if any([x in block["nickname"] for x in never_drop]):
        return "0, 0, 1, 0, 2, 1"
    # Item should always be dropped
    if any([x in block["nickname"] for x in always_drop]):
        return "100, 0, 1, 0, 2, 1"
    # Item should be dropped at the specified rate, defaulting to 0 if empty, missing, or malformed
    drop_properties = block_get(block, keyword = "drop_properties", default = "0, 0, 1, 0, 2, 1") # maybe missing
    if len(drop_properties) == 0 or drop_properties in ["nan", None]: # empty
        return "0, 0, 1, 0, 2, 1"
    elif len([n.strip() for n in drop_properties.split(",")]) != 6: # malformed
        print(f"WARNING: Dropping malformed drop_properties entry '{drop_properties}' of {block['nickname']} and defaulting to '0, 0, 1, 0, 2, 1'.")
        return "0, 0, 1, 0, 2, 1"
    else:
        try:
            assert int(drop_properties.split(",")[0].strip()) >= 0 and int(drop_properties.split(",")[0].strip()) <= 100 # malformed
            return drop_properties
        except:
            print(f"WARNING: Dropping malformed drop_properties entry '{drop_properties}' of {block['nickname']} and defaulting to '0, 0, 1, 0, 2, 1'.")
            return "0, 0, 1, 0, 2, 1"

def parse_all_files():
    
    all_blocks = []
    
    for file, block_names in tqdm(file_map.items()):
        # parse out all blocks
        start_lines, lines, blocks, nicknames = parse_blocks(file)
        blocks = [block for b, block in blocks.items()]
        
        # drop wrong block type
        blocks = [block for block in blocks if block["type"] in file_map[file]] 
        
        # if its a Munition/Mine/CM, it should require_ammo - if not, it should be lootable - else discard
        blocks = [
            block for block in blocks if (
            block["type"] in ["[CounterMeasure]", "[Mine]", "[Munition]"] and coerce_str_to_bool(block_get(block, keyword = "requires_ammo", default = True)) is True
            ) or (
            block["type"] not in ["[CounterMeasure]", "[Mine]", "[Munition]"] and coerce_str_to_bool(block_get(block, keyword = "lootable", default = True)) is True
            )]
        
        all_blocks.extend(blocks)
        
    return all_blocks
        
def generate_lootprops(target_file = "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\MISSIONS\\lootprops_gen.ini"):
    
    print("Generating lootprops from configurated files ...")
    all_blocks = parse_all_files()
    with open(target_file, "w") as o:
        for line in autogen_comment:
            o.write(f"{line}\n")
        o.write("\n")
        for block in all_blocks:
            o.write(f"\n\n[mLootProps]\nnickname = {block['nickname']}\ndrop_properties = {get_drop_properties(block)}\n")

if __name__ == "__main__":
    
    generate_lootprops(target_file = "D:\\GitHub\\fl_parity\\mod-assets\\DATA\\MISSIONS\\lootprops_gen.ini")