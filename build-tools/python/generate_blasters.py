import pandas as pd
from collections import OrderedDict

from ini_utils import CSVError, clean_unnamed_wip_empty, write_block

# 
HP_Types = {
    "S Energy": "hp_gun_special_01",
    "M Energy": "hp_gun_special_02",
    "L Energy": "hp_gun_special_03",
}

def make_scaling_rules(raw_csv):
    # TODO: make me
    return raw_csv

def create_equip_blocks(blaster, variant, multiplicity, scaling_rules):
    
    # Hash out calculated values
    if blaster["Overrides"] == "" or pd.isna(blaster["Overrides"]):
        nickname = f"bm_{blaster['Family Shorthand']}_{blaster['Identifier']}_{multiplicity}x_{variant['Variant Shorthand']}"
    else:
        nickname = blaster["Overrides"]
        
    if "\n" in blaster["Damage / rd"]:
        hull_damage, energy_damage = tuple(float(d) for d in blaster["Damage / rd"].split("\n"))
    else:
        hull_damage, energy_damage = float(blaster["Damage / rd"]), float(blaster["Damage / rd"])
        
    hull_damage = hull_damage * (1 + 0.01*variant["Variant Damage +%"]) * multiplicity     # /rd
    energy_damage = energy_damage * (1 + 0.01*variant["Variant Damage +%"]) * multiplicity # /rd
    power_usage = (
            blaster["Energy Cost / rd"] * 
            blaster["Refire (rds / s)"] * 
            (1 + 0.01*variant["Variant Energy Usage +%"]) * 
            multiplicity * 
            scaling_rules[f"{multiplicity}x Energy Factor"]
            ) # /s
    muzzle_velocity = blaster["muzzle_velocity"] * (1 + 0.01*variant["Variant Muzzle Velocity +%"])
    effective_range = blaster["range"] * (1 + 0.01*variant["Variant Range +%"])
    refire_rate = blaster["Refire (rds / s)"] * (1 + 0.01*variant["Variant Refire Rate +%"]) # /s
    
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
        "lifetime": effective_range / muzzle_velocity,
        "force_gun_ori": "false",
        "mass": 1
    })
    
    # Create gun block
    gun_block = OrderedDict({
        "nickname": nickname,
        "ids_name": blaster["IDS Name"],      #TODO: Find/make the appropriate infocard/name on the fly
        "ids_info": blaster["IDS Info"]+1000,
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
        "hp_gun_type": HP_Types[blaster["HP_Type"]],
        "damage_per_fire": 0,
        "power_usage": power_usage,
        "refire_delay": 1. / refire_rate,
        "muzzle_velocity": muzzle_velocity,
        "use_animation": "Sc_fire",
        "toughness": blaster["Toughness Index"] * multiplicity * variant["Toughness Modifier"],
        "flash_particle_name": blaster["Flash Particle Name"],
        "flash_radius": 15,
        "light_anim": "l_gun01_flash", #TODO: Is this right?
        "projectile_archetype": f"bm_{blaster['Family Shorthand']}_{blaster['Identifier']}_{multiplicity}x_{variant['Variant Shorthand']}_ammo",
        "separation_explosion": "sever_debris",
        "auto_turret": "false",
        "turn_rate": 90,
        "lootable": "false",
        "LODranges": "0, 20, 60, 100",
    })
    
    return f"{nickname}_ammo", munition_block, nickname, gun_block

def create_blasters(
    blaster_csv: str, 
    variant_csv: str, 
    scaling_rules_csv: str,
    ini_out_file: str
    ):
    
    # Get CSVs
    try:
        blasters = pd.read_csv(blaster_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {blaster_csv} couldn't be read and is probably borked.")
    try:
        variants = pd.read_csv(variant_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {variant_csv} couldn't be read and is probably borked.")
    try:
        scaling_rules_raw = pd.read_csv(scaling_rules_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {scaling_rules_csv} couldn't be read and is probably borked.")

    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    blasters = clean_unnamed_wip_empty(blasters)
    variants = clean_unnamed_wip_empty(variants)
    scaling_rules_raw = clean_unnamed_wip_empty(scaling_rules_raw)

    scaling_rules = make_scaling_rules(scaling_rules_raw)
    
    # Split off override entries
    blasters["Overrides"] = blasters["Overrides"].strip("\n").strip("\r")
    is_base = (blasters["Overrides"] == "" or pd.isna(blasters["Overrides"]))
    base_blasters = blasters[is_base]
    override_blasters = blasters[~is_base]
    
    writable_munition_blocks = OrderedDict()
    writable_gun_blocks = OrderedDict()
    
    # Iterate over all blasters and variants
    for blaster in base_blasters.iterrows():
        
        for variant in variants.iterrows():
            
            for multiplicity in ([1, 2, 3] if blaster["HP Type"] == "S Energy" else [1]):
                
                munition_name, munition_block, gun_name, gun_block = create_equip_blocks(blaster, variant, multiplicity, scaling_rules)
                writable_munition_blocks[munition_name] = munition_block
                writable_gun_blocks[gun_name] = gun_block
                
                # TODO: Infocard?
                
    for override_blaster in override_blasters.iterrows():
        
        munition_name, munition_block, gun_name, gun_block = create_equip_blocks(blaster, variant, multiplicity, scaling_rules)
        writable_munition_blocks[munition_name] = munition_block
        writable_gun_blocks[gun_name] = gun_block
        
                # TODO: Infocard?
    
    # Assume file exists already, append to file
    with open(ini_out_file, "a", encoding = "utf-8") as out:
        for munition_name, munition_block in writable_munition_blocks.items():
            out.write(f"[Munition]\n")
            for key, value in munition_block.items():
                out.write(f"{key} = {str(value)}\n")
            out.write("\n")
        for gun_name, gun_block in writable_gun_blocks.items():
            out.write(f"[Gun]\n")
            for key, value in munition_block.items():
                out.write(f"{key} = {str(value)}\n")
            out.write("\n")
    
    # TODO: Make infocards (calculate DPS, EPS, IDS Name, IDS Info)
    # TODO: Make goods entries
    # TODO: Make NPC variants
    # TODO: Edit template so that only non-variant inis are treated regularly, while PC/NPC Blasters (and Aux Weapons?) get variants