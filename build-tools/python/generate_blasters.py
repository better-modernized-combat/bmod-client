import pandas as pd
from collections import OrderedDict
from copy import deepcopy
from itertools import combinations
from tqdm.auto import tqdm
import re

from argparse import ArgumentParser

from defaults import *
from ini_utils import CSVError, clean_unnamed_wip_empty
from generate_infocards import FRC_Entry, generate_infocard_entry, write_infocards_to_frc

# FIXME turrets
# Currently supported multiplicities
supported_multiplicities = [(1, False), (2, False), (3, False), (3, True)]

def dfloat(s: str):
    if isinstance(s, str):
        return float(s.replace(",", "."))
    elif isinstance(s, int) or isinstance(s, float):
        return float(s)
    else:
        raise TypeError(f"dfloat can't be called on type {type(s)}, only float (noop), int, or str.")

def make_scaling_rules(raw_csv: pd.DataFrame):
    one_x_rules = pd.DataFrame({
        "Rule": ["1x Damage Factor", "1x Energy Factor", "1x Hardpoint", "1x Cost Factor"],
        "Entry": ["1.0", "1.0", "S Energy", "1.0"],
        "Comment": ["", "", "", ""]
        })
    updated_rules = pd.concat([raw_csv, one_x_rules], ignore_index = True)
    rules_dict = dict(zip(updated_rules["Rule"], updated_rules["Entry"]))
    return rules_dict

def create_blaster_ammo_blocks(blaster: dict, variant: dict, multiplicity: int, scaling_rules: dict, idx: int, is_turret: bool, is_override: bool = False):
    
    # Turrets are all multiplicity 3, if this ever changes, reminder to FIXME turrets
    if is_turret and multiplicity != 3:
        raise NotImplementedError("Time to think about how to do turrets properly.")
    
    # Hash out calculated values
    hull_damage, energy_damage = dfloat(blaster["Hull DMG / rd"]), dfloat(blaster["Energy DMG / rd"])
        
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
    
    cost = int(dfloat(blaster["Cost"]) * dfloat(variant["Cost Modifier"]))
    
    # HP Type guessing
    if is_turret:
        hp_type_guess = HP_Types["PD Turret"] # FIXME turrets
        mt_name = "3xT"
    elif blaster["HP Type"] != "S Energy":
        hp_type_guess = HP_Types[blaster["HP Type"]]
        mt_name = "1x"
    else:
        hp_type_guess = HP_Types[{1: "S Energy", 2: "M Energy", 3: "L Energy"}[multiplicity]]
        mt_name = f"{multiplicity}x"
        
    # Get nickname from override or construct it
    if not is_override or isinstance(blaster["Overrides"], float):
        nickname = f"bm_{blaster['Family Shorthand']}_{blaster['Identifier']}_{mt_name}_{variant['Variant Shorthand']}"    
    else:
        nickname = blaster["Overrides"]
    
    # Create ammunition block
    munition_block = OrderedDict({
        "nickname": f"{nickname}_ammo",
        "hp_type": "hp_gun", #TODO: Is this right?
        "requires_ammo": "false",
        "hit_pts": 2,
        "hull_damage": hull_damage,
        "energy_damage": energy_damage,
        "weapon_type": blaster["Weapon Type"],
        "one_shot_sound": f"{blaster['Fire Sound']}", # TODO: generate and use {variant['Variant Audio Shorthand']}
        "munition_hit_effect": blaster["Hit Effect"],
        "const_effect": f"{blaster['Projectile Effect']}", # TODO: generate and use {variant['Variant Visual Shorthand']}
        "lifetime": lifetime,
        "force_gun_ori": "false",
        "mass": 1
    })
    
    # Create gun block
    gun_block = OrderedDict({
        "nickname": nickname,
        "ids_name": idx,      #TODO: Find/make the appropriate infocard/name on the fly
        "ids_info": idx+1,
        "DA_archetype": (blaster["Gun Archetype"] if not is_turret else "BMOD\EQUIPMENT\MODELS\TURRETS\bm_f_fleet_turret_twin.cmp"), # FIXME turrets
        "material_library": (blaster["Material Library"] if not is_turret else "material_library = equipment\models\li_turret.mat"), # FIXME turrets
        "HP_child": "HPConnect",
        "hit_pts": blaster["Gun HP"],
        "explosion_resistance": 0,
        "debris_type": "debris_normal",
        "parent_impulse": 20,
        "child_impulse": 80,
        "volume": 0 * multiplicity,
        "mass": 10 * multiplicity,
        "hp_gun_type": (HP_Types[blaster["HP Type"]] if is_override else hp_type_guess),
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
        "; cost": cost,
    })
    if not pd.isna(blaster["Dispersion Angle"]) and not blaster["Dispersion Angle"] == "":
        gun_block["dispersion_angle"] = dfloat(blaster["Dispersion Angle"])
    
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

def write_ammo_and_guns(ini_out_file, ammo_dict, gun_dict, npc_ammo_dict, npc_gun_dict):
    
    with open(ini_out_file, "w", encoding = "utf-8") as out:
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
            
        for munition_name, munition_block in npc_ammo_dict.items():
            out.write(f"[Munition]\n")
            for key, value in munition_block.items():
                #print(f"{key} = {str(value)}\n")
                out.write(f"{key} = {str(value)}\n")
            out.write("\n")
        for gun_name, gun_block in npc_gun_dict.items():
            out.write(f"[Gun]\n")
            for key, value in gun_block.items():
                out.write(f"{key} = {str(value)}\n")
            out.write("\n")

def create_good(
    blaster: dict,
    variant: dict,
    internal_name: str,
    ids_name: int,
    mp: int,
    is_turret: bool
):
    
    # Guess item icon, if necessary
    if pd.isna(blaster["Item Icon"]) or blaster["Item Icon"] == "":
        if any(x in variant["Display Name Suffix"] for x in ["[+]", "[♠]"]):
            pnm = "-plus"
        elif "[-]" in variant["Display Name Suffix"]:
            pnm = "-minus"
        else:
            pnm = ""
        size = {1: "s", 2: "m", 3: "l"}[mp]
        item_icon = f"BMOD\\EQUIPMENT\\ICONS\\WEAPONS\\BLASTERS\\blaster-{'fleet-' if is_turret else ''}{size}{pnm}.3db"
    else:
        item_icon = blaster["Item Icon"]
    
    good = OrderedDict({
        "nickname": internal_name,
        "equipment": internal_name,
        "category": "equipment",
        "price": int(dfloat(blaster["Cost"]) * dfloat(variant["Cost Modifier"])),
        "item_icon": item_icon,
        "combinable": False,
        "ids_name": ids_name,
        "shop_archetype": blaster["Gun Archetype"],
        "material_library": blaster["Material Library"]
    })
    
    return good

def write_blaster_goods(
    goods_out: str,
    goods: dict,
):
    with open(goods_out, "w") as out:
        for line in autogen_comment:
            out.write(line+"\n")
        out.write("\n")
        for idx, good in goods.items():
            out.write("[Good]\n")
            out.writelines([f"{key} = {val}\n" for key, val in good.items()])
            out.write("\n\n")

def fill_admin_store(
    admin_store_location: str,
    admin_store_items: dict,
):
    
    with open(admin_store_location, "r") as file:
        
        content = file.read()
        store_pattern = "(?<=;;; ADMIN STORE ;;;\n)((.|\n)*?)(?=;;; ADMIN STORE ;;;\n)"
        store = [f"MarketGood = {nickname}, 0, -1, 10, 10, 0, 1" for nickname in admin_store_items]
        replacement = "\n".join(store)+"\n"
        new_content = re.sub(store_pattern, replacement, content)
        
    with open(admin_store_location, "w") as file:
        
        file.write(new_content)

def sanity_check(
    blasters: dict, 
    munitions: dict,
    balance_notification: str = "warn",
    check_multiplicity: bool = True,
    check_variants: bool = False,
    check_zeros: bool = True,
    include_cost: bool = False,
    include_hardpoint_size: bool = True,
    ):
    """
    If a gun has stats that are better or equal across the board, compared to a gun of the same multiplicity,
    either print a warning or raise a ValueError.
    
    balance_notification - Must be 'raise' or 'warn'. If 'raise', raises a ValueError after printing all balance problems to the console. If 'warn', only print. Detault is 'warn'.
    check_multiplicity - If True, extend the pairings by also comparing each multiplicity. Default is True.
    check_variants - If True, check for all variant pairings whether they are balanced as well. This will usually produce lots of warnings and is thus turned off by default.
    check_zeros - If True, also test if any 0 shows up in a gun stat. If so, count it as unbalanced. Default is True.
    include_cost - If True, a weapon is still balanced iff it costs more than its inferior counterpart. Default is False, because we like sidegrades more than straight upgrades.
    include_hardpoint_size - If True, a weapon is still balanced iff it uses a larger hardpoint than its inferior counterpart. Default is True.
    """
    
    assert balance_notification in ["raise", "warn"]
    
    balancing_sane = True
    
    # Iterate over all weapon pairings
    print("INFO: Weapon Balance Sanity Check in progress ...")
    for b1, b2 in tqdm(combinations(blasters, r = 2), total = int(len(blasters)*(len(blasters)-1)/2)):
        
        n1, n2 = blasters[b1]["nickname"], blasters[b2]["nickname"]
        
        # Skip variants?
        if check_variants is False and ("x_x" in n1 or "xT_x" in n1 or "x_x" in n2 or "xT_x" in n2):
            continue
        
        # Skip weapon pairings that have ...
        for m in ["3xT", "1x", "2x", "3x"]: # FIXME turrets
            if m in n1:
                m1 = m
                break
        for m in ["3xT", "1x", "2x", "3x"]: # FIXME turrets
            if m in n2:
                m2 = m
                break
        # different multiplicity?
        if check_multiplicity is False and (m in n1 and not m in n2):
            continue
        # the same base weapon, and are just 3x and turret, as those are naturally equal
        if ((m1 == "3x" and m2 == "3xT") or (m1 == "3xT" and m1 == "3x")) and n1.split(m1)[0] == n2.split(m2)[0]:
            continue
        
        hd1, hd2 = munitions[b1+"_ammo"]["hull_damage"], munitions[b2+"_ammo"]["hull_damage"]
        ed1, ed2 = munitions[b1+"_ammo"]["energy_damage"], munitions[b2+"_ammo"]["energy_damage"]
        mv1, mv2 = blasters[b1]["muzzle_velocity"], blasters[b2]["muzzle_velocity"]
        er1, er2 = mv1 * munitions[b1+"_ammo"]["lifetime"], mv2 * munitions[b2+"_ammo"]["lifetime"]
        rr1, rr2 = 1. / blasters[b1]["refire_delay"], 1. / blasters[b2]["refire_delay"]
        pu1, pu2 = blasters[b1]["power_usage"] / rr1, blasters[b2]["power_usage"] / rr2
        c1, c2 = blasters[b1]["; cost"], blasters[b2]["; cost"]
        hp1, hp2 = HP_Size[blasters[b1]["hp_gun_type"]], HP_Size[blasters[b2]["hp_gun_type"]]
        
        # Compare stats. If a stat is not required, set it to one of the other stats, so the result doesn't change.
        b1_eq_b2 = all([
            hd1 == hd2, 
            ed1 == ed2, 
            pu1 == pu2, 
            mv1 == mv2, 
            er1 == er2, 
            rr1 == rr2, 
            (hd1 == hd2 if include_cost is False else c1 == c2),
            (hd1 == hd2 if include_hardpoint_size is False else hp1 == hp2),
        ])
        if b1_eq_b2 is True:
            balancing_sane = False
            print(f"WARNING: Balance problem detected. Weapon {n1} is precisely equal to weapon {n2}.")
            continue
        b1_gt_b2 = all([
            hd1 >= hd2,
            ed1 >= ed2,
            pu1 <= pu2,
            mv1 >= mv2,
            er1 >= er2,
            rr1 >= rr2,
            (hd1 >= hd2 if include_cost is False else c1 <= c2),
            (hd1 >= hd2 if include_hardpoint_size is False else hp1 <= hp2),
        ])
        if b1_gt_b2 is True:
            balancing_sane = False
            print(f"WARNING: Balance problem detected. Weapon {n1} is strictly better than weapon {n2}.")
            print(f"{blasters[b1]['hp_gun_type']}, {blasters[b2]['hp_gun_type']}")
            continue
        b2_gt_b1 = all([
            hd2 >= hd1,
            ed2 >= ed1,
            pu2 <= pu1,
            mv2 >= mv1,
            er2 >= er1,
            rr2 >= rr1,
            (hd2 >= hd1 if include_cost is False else c2 <= c1),
            (hd2 >= hd1 if include_hardpoint_size is False else hp2 <= hp1),
        ])
        if b2_gt_b1 is True:
            balancing_sane = False
            print(f"WARNING: Balance problem detected. Weapon {n2} is strictly better than weapon {n1}.")
            print(f"{blasters[b1]['hp_gun_type']}, {blasters[b2]['hp_gun_type']}")
            continue
        if check_zeros is True:
            for stat in [hd1, ed1, pu1, mv1, er1, rr1]:
                if stat in [0, "0"]:
                    balancing_sane = False
                    print(f"WARNING: Balance problem detected. Weapon {n1} has a zero stat.")
            for stat in [hd2, ed2, pu2, mv2, er2, rr2]:
                if stat in [0, "0"]:
                    balancing_sane = False
                    print(f"WARNING: Balance problem detected. Weapon {n2} has a zero stat.")
        
    if balancing_sane is False:
        if balance_notification == "raise":
            raise ValueError("ERROR: Weapons are unbalanced. Raising error to prevent build.")
        else:
            print("WARNING: Weapons are unbalanced, see build logs.")
    else:
        print("INFO: All weapons have passed sanity check.")

def create_blasters(
    blaster_csv: str, 
    variant_csv: str, 
    scaling_rules_csv: str,
    pc_blasters_out: str,
    blaster_goods_out: str,
    blaster_infocards_out: str,
    weapon_sanity_check: bool,
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
    is_override = blasters["Overrides"].apply(lambda x: False if pd.isna(x) or x == "" else True)
    base_blasters = blasters[~is_override]
    override_blasters = blasters[is_override]
    
    writable_munition_blocks = OrderedDict()
    writable_gun_blocks = OrderedDict()
    writable_npc_munition_blocks = OrderedDict()
    writable_npc_gun_blocks = OrderedDict()
    writable_infocards = OrderedDict()
    writable_goods = OrderedDict()
    
    # Iterate over all blasters and variants
    bd = base_blasters.to_dict(orient = "index").items()
    od = override_blasters.to_dict(orient = "index").items()
    vd = variants.to_dict(orient = "index").items()
    
    for b, blaster in bd:
        
        for v, variant in vd:
            
            # Save the base variant settings to use for overrides
            if v == 0:
                base_variant = deepcopy(variant)
            
            for n, (multiplicity, is_turret) in enumerate(
                supported_multiplicities if blaster["HP Type"] == "S Energy" and blaster["Family Shorthand"] not in ["aux", "auxf"] # ugly band-aid fix for S Lasers
                else [(1, blaster["HP Type"] == "PD Turret")] # FIXME Turrets
                ):
                
                i_counter = int(blaster["IDS Name"]) + 4 * (v*len(supported_multiplicities) + n)
                
                munition_name, munition_block, npc_munition_block, gun_name, gun_block, npc_gun_block = create_blaster_ammo_blocks(
                    blaster = blaster, 
                    variant = variant, 
                    multiplicity = multiplicity, 
                    scaling_rules = scaling_rules,
                    idx = i_counter,
                    is_turret = is_turret,
                    is_override = False,
                    )
                writable_munition_blocks[munition_name] = munition_block
                writable_gun_blocks[gun_name] = gun_block
                writable_npc_munition_blocks[munition_name] = npc_munition_block
                writable_npc_gun_blocks[gun_name] = npc_gun_block
                
                # Generate Infocard FRC entries
                display_name, formatted_infocard_content = generate_infocard_entry(
                    name = blaster["Weapon Name"],
                    long_name = blaster["Long Name"],
                    info = blaster["Base Infocard"],
                    is_turret = is_turret,
                    mp = multiplicity,
                    mp_info = infocard_boilerplate[(multiplicity, is_turret)],
                    variant_sh = variant["Variant Shorthand"],
                    variant_desc = variant["Variant Description"],
                    variant_info = variant["Variant Infocard Paragraph"],
                    variant_display = variant["Display Name Suffix"],
                )
                writable_infocards[i_counter] = FRC_Entry(typus = "S", idx = blaster["IDS Name"], content = display_name)
                writable_infocards[i_counter+1] = FRC_Entry(typus = "H", idx = blaster["IDS Name"], content = formatted_infocard_content)
                writable_infocards[i_counter+2] = FRC_Entry(typus = "S", idx = blaster["IDS Name"], content = display_name)                 # NPC version
                writable_infocards[i_counter+3] = FRC_Entry(typus = "H", idx = blaster["IDS Name"], content = formatted_infocard_content)   # NPC version
                
                # Generate blaster goods entries
                writable_goods[i_counter] = create_good(blaster = blaster, variant = variant, internal_name = gun_block["nickname"], ids_name = i_counter, mp = multiplicity, is_turret = is_turret)
                writable_goods[i_counter+2] = create_good(blaster = blaster, variant = variant, internal_name = npc_gun_block["nickname"], ids_name = i_counter+2, mp = multiplicity, is_turret = is_turret) # NPC version
                
    for o, override_blaster in od:
        
        i_counter = int(blaster["IDS Name"]) + 4 * o
        
        munition_name, munition_block, npc_munition_block, gun_name, gun_block, npc_gun_block = create_blaster_ammo_blocks(
            blaster = override_blaster, 
            variant = base_variant,
            multiplicity = 1,
            scaling_rules = scaling_rules,
            idx = i_counter,
            is_turret = (override_blaster["HP Type"] == "PD Turret"), # FIXME turrets
            is_override = True
            )
        writable_munition_blocks[munition_name] = munition_block
        writable_gun_blocks[gun_name] = gun_block
        writable_npc_munition_blocks[munition_name] = npc_munition_block
        writable_npc_gun_blocks[gun_name] = npc_gun_block
        
        # Generate Infocard FRC entries
        display_name, formatted_infocard_content = generate_infocard_entry(
            name = blaster["Weapon Name"],
            long_name = blaster["Long Name"],
            info = blaster["Base Infocard"],
            is_turret = is_turret,
            mp = multiplicity,
            mp_info = infocard_boilerplate[(multiplicity, is_turret)],
            variant_sh = variant["Variant Shorthand"],
            variant_desc = variant["Variant Description"],
            variant_info = variant["Variant Infocard Paragraph"],
            variant_display = variant["Display Name Suffix"],
        )
        writable_infocards[i_counter] = FRC_Entry(typus = "S", idx = blaster["IDS Name"], content = display_name)
        writable_infocards[i_counter+1] = FRC_Entry(typus = "H", idx = blaster["IDS Name"], content = formatted_infocard_content)
        writable_infocards[i_counter+2] = FRC_Entry(typus = "S", idx = blaster["IDS Name"], content = display_name)
        writable_infocards[i_counter+3] = FRC_Entry(typus = "H", idx = blaster["IDS Name"], content = formatted_infocard_content)
        
        # Generate blaster goods entries
        writable_goods[i_counter] = create_good(blaster = blaster, variant = variant, internal_name = gun_block["nickname"], ids_name = i_counter, mp = multiplicity, is_turret = is_turret)
        writable_goods[i_counter] = create_good(blaster = blaster, variant = variant, internal_name = npc_gun_block["nickname"], ids_name = i_counter + 2, mp = multiplicity, is_turret = is_turret) # NPC version
                
    # Sanity check weapon balance. NPC weapon balance is implied by PC weapon balance (probably), sorta irrelevant, and therefore ignored.
    if weapon_sanity_check is True:
        sanity_check(writable_gun_blocks, writable_munition_blocks)
    
    # Write to inis/frc.
    write_ammo_and_guns(pc_blasters_out, writable_munition_blocks, writable_gun_blocks, writable_npc_munition_blocks, writable_npc_gun_blocks)
    write_infocards_to_frc(blaster_infocards_out, writable_infocards)
    write_blaster_goods(blaster_goods_out, writable_goods)
    
    # Fill admin store with goodies (for testing)
    fill_admin_store("mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_market_misc.ini", writable_gun_blocks)
    
    # TODO: Edit template to separate variant-able gear and non-variantable gear
    # TODO: generate the following corresponding files based on the name of the gun:
    ### - flash_particle_name, const_effect, munition_hit_effect, one_shot_sound
    
if __name__ == "__main__":
    
    parser = ArgumentParser()
    parser.add_argument("--blaster_csv", dest = "blaster_csv", type = str)
    parser.add_argument("--variant_csv", dest = "variant_csv", type = str)
    parser.add_argument("--scaling_rules_csv", dest = "scaling_rules_csv", type = str)
    parser.add_argument("--pc_blasters_out", dest = "pc_blasters_out", type = str)
    parser.add_argument("--blaster_goods_out", dest = "blaster_goods_out", type = str)
    parser.add_argument("--blaster_infocards_out", dest = "blaster_infocards_out", type = str)
    parser.add_argument("--weapon_sanity_check", dest = "weapon_sanity_check", action = "store_true", default = False)
    
    args = parser.parse_args()
    
    create_blasters(
        blaster_csv = args.blaster_csv,
        variant_csv = args.variant_csv,
        scaling_rules_csv = args.scaling_rules_csv,
        pc_blasters_out = args.pc_blasters_out,
        blaster_goods_out = args.blaster_goods_out,
        blaster_infocards_out = args.blaster_infocards_out,
        weapon_sanity_check = args.weapon_sanity_check,
        )