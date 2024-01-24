import pandas as pd
from collections import OrderedDict
from copy import deepcopy

from argparse import ArgumentParser

from ini_utils import CSVError, clean_unnamed_wip_empty, write_block

HP_Types = {
    "S Energy": "hp_gun_special_1",
    "M Energy": "hp_gun_special_2",
    "L Energy": "hp_gun_special_3",
}

def dfloat(s: str):
    if isinstance(s, str) and "," in s:
        return float(s.replace(",", "."))
    else:
        return float(s)

def make_scaling_rules(raw_csv: pd.DataFrame):
    one_x_rules = pd.DataFrame({
        "Rule": ["1x Damage Factor", "1x Energy Factor", "1x Hardpoint", "1x Cost Factor"],
        "Entry": ["1.0", "1.0", "S Energy", "1.0"],
        "Comment": ["", "", "", ""]
        })
    updated_rules = pd.concat([raw_csv, one_x_rules], ignore_index = True)
    rules_dict = dict(zip(updated_rules["Rule"], updated_rules["Entry"]))
    return rules_dict

def create_equip_blocks(blaster, variant, multiplicity, scaling_rules):
    
    # Hash out calculated values
    if blaster["Overrides"] == "" or pd.isna(blaster["Overrides"]):
        is_override = False
        nickname = f"bm_{blaster['Family Shorthand']}_{blaster['Identifier']}_{multiplicity}x_{variant['Variant Shorthand']}"
    else:
        is_override = True
        nickname = blaster["Overrides"]
        
    if "\n" in blaster["Damage / rd"]:
        hull_damage, energy_damage = tuple(dfloat(d) for d in blaster["Damage / rd"].split("\n"))
    else:
        hull_damage, energy_damage = float(blaster["Damage / rd"]), dfloat(blaster["Damage / rd"])
        
    hull_damage = hull_damage * (1 + 0.01*dfloat(variant["Variant Damage +%"])) * multiplicity     # /rd
    energy_damage = energy_damage * (1 + 0.01*dfloat(variant["Variant Damage +%"])) * multiplicity # /rd
    power_usage = (
            dfloat(blaster["Energy Usage / rd"]) * 
            dfloat(blaster["Refire (rds / s)"]) * 
            (1 + 0.01*dfloat(variant["Variant Energy Usage +%"])) * 
            multiplicity * 
            dfloat(scaling_rules[f"{multiplicity}x Energy Factor"])
            ) # /s
    muzzle_velocity = dfloat(blaster["Muzzle Velocity"]) * (1 + 0.01*dfloat(variant["Variant Muzzle Velocity +%"]))
    effective_range = dfloat(blaster["Range"]) * (1 + 0.01*dfloat(variant["Variant Range +%"]))
    refire_rate = dfloat(blaster["Refire (rds / s)"]) * (1 + 0.01*dfloat(variant["Variant Refire Rate +%"])) # /s
    lifetime = effective_range / muzzle_velocity
    
    # Create ammunition block
    munition_block = OrderedDict({
        "nickname": f"{nickname}_ammo",
        "hp_type": "hp_gun", #TODO: Is this right?
        "requires_ammo": "false",
        "hit_pts": 2,
        "hull_damage": hull_damage,
        "energy_damage": energy_damage,
        "weapon_type": blaster["Weapon Type"],
        "one_shot_sound": f"{blaster['Fire Sound']}{variant['Variant Audio Shorthand']}",
        "munition_hit_effect": blaster["Hit Effect"],
        "const_effect": f"{blaster['Projectile Effect']}{variant['Variant Visual Shorthand']}",
        "lifetime": lifetime,
        "force_gun_ori": "false",
        "mass": 1
    })
    
    # Create gun block
    gun_block = OrderedDict({
        "nickname": nickname,
        "ids_name": blaster["IDS Name"],      #TODO: Find/make the appropriate infocard/name on the fly
        "ids_info": str(int(blaster["IDS Name"])+1000),
        "DA_archetype": blaster["Gun Archetype"],
        "material_library": blaster["Material Library"],
        "HP_child": "HPConnect",
        "hit_pts": blaster["Gun HP"],
        "explosion_resistance": 0,
        "debris_type": "debris_normal",
        "parent_impulse": 20,
        "child_impulse": 80,
        "volume": 0 * multiplicity,
        "mass": 10 * multiplicity,
        "hp_gun_type": (HP_Types[blaster["HP_Type"]] if is_override else HP_Types[{1: "S Energy", 2: "M Energy", 3: "L Energy"}[multiplicity]]),
        "damage_per_fire": 0,
        "power_usage": power_usage,
        "refire_delay": 1. / refire_rate,
        "muzzle_velocity": muzzle_velocity,
        "use_animation": "Sc_fire",
        "toughness": float(blaster["Toughness Index"]) * multiplicity * dfloat(variant["Toughness Modifier"]),
        "flash_particle_name": blaster["Flash Particle Name"],
        "flash_radius": 15,
        "light_anim": "l_gun01_flash", #TODO: Is this right?
        "projectile_archetype": f"bm_{blaster['Family Shorthand']}_{blaster['Identifier']}_{multiplicity}x_{variant['Variant Shorthand']}_ammo",
        "separation_explosion": "sever_debris",
        "auto_turret": "false",
        "turn_rate": blaster["Turn Rate"],
        "lootable": "false",
        "LODranges": "0, 20, 60, 100",
    })
    
    # Create NPC blocks
    npc_ammo_nickname = nickname[:3]+"npc_"+nickname[3:]+"_ammo"
    npc_gun_nickname = nickname[:3]+"npc_"+nickname[3:]
    npc_hull_damage = hull_damage * dfloat(scaling_rules["NPC Damage Factor"])
    npc_energy_damage = energy_damage * dfloat(scaling_rules["NPC Damage Factor"])
    npc_power_usage = power_usage * dfloat(scaling_rules["NPC Energy Factor"])
    npc_effective_range = effective_range * dfloat(scaling_rules["NPC Range Factor"])
    npc_muzzle_velocity = muzzle_velocity * dfloat(scaling_rules["NPC Muzzle Velocity Factor"])
    npc_lifetime = npc_effective_range / npc_muzzle_velocity
    
    npc_munition_block = deepcopy(munition_block)
    npc_munition_block.update({"nickname": npc_ammo_nickname, "hull_damage": npc_hull_damage, "energy_damage": npc_energy_damage, "lifetime": npc_lifetime})
    npc_gun_block = deepcopy(gun_block)
    npc_gun_block.update({"nickname": npc_gun_nickname, "power_usage": npc_power_usage, "muzzle_velocity": npc_muzzle_velocity})
    
    return f"{nickname}_ammo", munition_block, npc_munition_block, nickname, gun_block, npc_gun_block

def write_ammo_and_guns(ini_out_file, ammo_dict, gun_dict):
        
    # Assume file exists already, append to file
    with open(ini_out_file, "a", encoding = "utf-8") as out:
        for munition_name, munition_block in ammo_dict.items():
            out.write(f"[Munition]\n")
            for key, value in munition_block.items():
                #print(f"{key} = {str(value)}\n")
                out.write(f"{key} = {str(value)}\n")
            out.write("\n")
        for gun_name, gun_block in gun_dict.items():
            out.write(f"[Gun]\n")
            for key, value in gun_block.items():
                out.write(f"{key} = {str(value)}\n")
            out.write("\n")

def create_blasters(
    blaster_csv: str, 
    variant_csv: str, 
    scaling_rules_csv: str,
    pc_blasters_out: str,
    npc_blasters_out: str
    ):
    
    # Get CSVs
    try:
        blasters = pd.read_csv(blaster_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {blaster_csv} couldn't be read and is probably borked.")
    try:
        variants = pd.read_csv(variant_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object, keep_default_na = False)
    except:
        raise CSVError(f"CSV {variant_csv} couldn't be read and is probably borked.")
    try:
        scaling_rules_raw = pd.read_csv(scaling_rules_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {scaling_rules_csv} couldn't be read and is probably borked.")

    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    blasters = clean_unnamed_wip_empty(blasters, name = blaster_csv)
    variants = clean_unnamed_wip_empty(variants, name = variant_csv)
    scaling_rules_raw = clean_unnamed_wip_empty(scaling_rules_raw, name = scaling_rules_csv)
    scaling_rules = make_scaling_rules(scaling_rules_raw)
    
    # Split off override entries
    #blasters["Overrides"] = blasters["Overrides"].strip("\n").strip("\r")
    is_base = (blasters["Overrides"].apply(lambda x: True if x == "" or pd.isna(x) else False))
    base_blasters = blasters[is_base]
    override_blasters = blasters[~is_base]
    
    writable_munition_blocks = OrderedDict()
    writable_gun_blocks = OrderedDict()
    writable_npc_munition_blocks = OrderedDict()
    writable_npc_gun_blocks = OrderedDict()
    
    # Iterate over all blasters and variants
    
    for _, blaster in base_blasters.to_dict(orient = "index").items():
        
        for _, variant in variants.to_dict(orient = "index").items():
            
            for multiplicity in ([1, 2, 3] if blaster["HP Type"] == "S Energy" else [1]):
                
                munition_name, munition_block, npc_munition_block, gun_name, gun_block, npc_gun_block = create_equip_blocks(blaster, variant, multiplicity, scaling_rules)
                writable_munition_blocks[munition_name] = munition_block
                writable_gun_blocks[gun_name] = gun_block
                writable_npc_munition_blocks[munition_name] = npc_munition_block
                writable_npc_gun_blocks[gun_name] = npc_gun_block
                
                # TODO: Infocard?
                
    for _, override_blaster in override_blasters.to_dict(orient = "index").items():
        
        munition_name, munition_block, npc_munition_block, gun_name, gun_block, npc_gun_block = create_equip_blocks(override_blaster, variant, multiplicity, scaling_rules)
        writable_munition_blocks[munition_name] = munition_block
        writable_gun_blocks[gun_name] = gun_block
        writable_npc_munition_blocks[munition_name] = npc_munition_block
        writable_npc_gun_blocks[gun_name] = npc_gun_block
        
                # TODO: Infocard?
    
    write_ammo_and_guns(pc_blasters_out, writable_munition_blocks, writable_gun_blocks)
    write_ammo_and_guns(npc_blasters_out, writable_npc_munition_blocks, writable_npc_gun_blocks)
    
    # TODO: Make infocards (calculate DPS, EPS, IDS Name, IDS Info, NPC/PC)
    # TODO: Make goods entries
    # TODO: Edit template so that only non-variant inis are treated regularly, while PC/NPC Blasters (and Aux Weapons?) get variants
    # TODO: generate the following fields and the corresponding files based on the name of the gun:
    ### - flash_particle_name, const_effect, munition_hit_effect, one_shot_sound
    
if __name__ == "__main__":
    
    parser = ArgumentParser()
    parser.add_argument("--blaster_csv", dest = "blaster_csv", type = str)
    parser.add_argument("--variant_csv", dest = "variant_csv", type = str)
    parser.add_argument("--scaling_rules_csv", dest = "scaling_rules_csv", type = str)
    parser.add_argument("--pc_blasters_out", dest = "pc_blasters_out", type = str)
    parser.add_argument("--npc_blasters_out", dest = "npc_blasters_out", type = str)
    
    args = parser.parse_args()
    
    create_blasters(
        blaster_csv = args.blaster_csv,
        variant_csv = args.variant_csv,
        scaling_rules_csv = args.scaling_rules_csv,
        pc_blasters_out = args.pc_blasters_out,
        npc_blasters_out = args.npc_blasters_out
        )