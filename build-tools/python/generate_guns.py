import pandas as pd
from collections import OrderedDict
from copy import deepcopy
from itertools import combinations
from tqdm.auto import tqdm
import re

from typing import List

from argparse import ArgumentParser

from defaults import *
from ini_utils import CSVError, clean_unnamed_wip_empty
from generate_infocards import FRC_Entry, generate_weapon_infocard_entry, generate_ammo_infocard_entry, write_infocards_to_frc

from utils import bcolors
# TODO: use bcolors for DEBUG/INFO/WARN/ERROR distinction

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

def create_blaster_ammo_blocks(weapon: dict, variant: dict, multiplicity: int, scaling_rules: dict, idx: int, is_turret: bool = False, is_override: bool = False):
    
    # Turrets are all multiplicity 3, if this ever changes, reminder to FIXME turrets
    if is_turret and multiplicity != 3:
        raise NotImplementedError("Time to think about how to do turrets properly.")
    
    # Hash out calculated values, or get them from the override
    if not is_override or isinstance(weapon["Overrides"], float):
        hull_damage, energy_damage = dfloat(weapon["Hull DMG / rd"]), dfloat(weapon["Energy DMG / rd"])
            
        hull_damage = hull_damage * (1 + 0.01*dfloat(variant["Variant Damage +%"])) * multiplicity     # /rd
        energy_damage = energy_damage * (1 + 0.01*dfloat(variant["Variant Damage +%"])) * multiplicity # /rd
        power_usage = (
                dfloat(weapon["Energy Usage / rd"]) *
                (1 + 0.01*dfloat(variant["Variant Energy Usage +%"])) * 
                dfloat(scaling_rules[f"{multiplicity}x Energy Factor"])
                )
        muzzle_velocity = dfloat(weapon["Muzzle Velocity"]) * (1 + 0.01*dfloat(variant["Variant Muzzle Velocity +%"]))
        effective_range = dfloat(weapon["Range"]) * (1 + 0.01*dfloat(variant["Variant Range +%"]))
        refire_rate = dfloat(weapon["Refire (rds / s)"]) * (1 + 0.01*dfloat(variant["Variant Refire Rate +%"])) # /s
        lifetime = effective_range / muzzle_velocity
        
        toughness = dfloat(weapon["Toughness Index"]) * multiplicity * dfloat(variant["Toughness Modifier"])
        cost = int(dfloat(weapon["Cost"]) * dfloat(variant["Cost Modifier"]))
    else:
        hull_damage, energy_damage = dfloat(weapon["Hull DMG / rd"]), dfloat(weapon["Energy DMG / rd"])
        power_usage = dfloat(weapon["Energy Usage / rd"])
        muzzle_velocity = dfloat(weapon["Muzzle Velocity"])
        effective_range = dfloat(weapon["Range"])
        refire_rate = dfloat(weapon["Refire (rds / s)"])
        lifetime = effective_range / muzzle_velocity
        
        toughness = dfloat(weapon["Toughness Index"])
        cost = int(dfloat(weapon["Cost"]))
    
    # HP Type guessing or get from override
    if not is_override or isinstance(weapon["Overrides"], float):
        if is_turret:
            hp_type_guess = HP_Types["PD Turret"] # FIXME turrets
            mt_name = "3xT"
        elif weapon["HP Type"] != "S Energy":
            hp_type_guess = HP_Types[weapon["HP Type"]]
            mt_name = "1x"
        else:
            hp_type_guess = HP_Types[{1: "S Energy", 2: "M Energy", 3: "L Energy"}[multiplicity]]
            mt_name = f"{multiplicity}x"
    else:
        hp_type_guess = HP_Types[weapon["HP Type"]]
        mt_name = f"{multiplicity}x"
        
    # Construct nickname or get from override
    if not is_override or isinstance(weapon["Overrides"], float):
        nickname = f"bm_{weapon['Family Shorthand']}_{weapon['Identifier']}_{mt_name}_{variant['Variant Shorthand']}"    
    else:
        nickname = weapon["Overrides"]
    
    # Create ammunition block
    munition_block = OrderedDict({
        "nickname": f"{nickname}_ammo",
        "hp_type": "hp_gun", #TODO: Is this right?
        "requires_ammo": "false",
        "hit_pts": 2,
        "hull_damage": hull_damage,
        "energy_damage": energy_damage,
        "weapon_type": weapon["Weapon Type"],
        "one_shot_sound": f"{weapon['Fire Sound']}", # TODO: generate and use {variant['Variant Audio Shorthand']}
        "munition_hit_effect": weapon["Hit Effect"],
        "const_effect": f"{weapon['Projectile Effect']}", # TODO: generate and use {variant['Variant Visual Shorthand']}
        "lifetime": lifetime,
        "force_gun_ori": "false",
        "mass": 1
    })
    
    # Create weapon block
    weapon_block = OrderedDict({
        "nickname": nickname,
        "ids_name": idx,
        "ids_info": idx+1,
        "DA_archetype": (weapon["Gun Archetype"] if not is_turret else "BMOD\\EQUIPMENT\\MODELS\\TURRETS\\bm_f_fleet_turret_twin.cmp"), # FIXME turrets
        "material_library": (weapon["Material Library"] if not is_turret else "equipment\\models\\li_turret.mat"), # FIXME turrets
        "HP_child": "HPConnect",
        "hit_pts": weapon["Gun HP"],
        "explosion_resistance": 0,
        "debris_type": "debris_normal",
        "parent_impulse": 20,
        "child_impulse": 80,
        "volume": 0 * multiplicity,
        "mass": 10 * multiplicity,
        "hp_gun_type": hp_type_guess,
        "damage_per_fire": 0,
        "power_usage": power_usage,
        "refire_delay": 1. / refire_rate,
        "muzzle_velocity": muzzle_velocity,
        "use_animation": "Sc_fire",
        "toughness": toughness,
        "flash_particle_name": weapon["Flash Particle Name"],
        "flash_radius": 15,
        "light_anim": weapon["Light Animation"],
        "projectile_archetype": f"{nickname}_ammo",
        "separation_explosion": "sever_debris",
        "auto_turret": "false",
        "turn_rate": weapon["Turn Rate"],
        "lootable": "false",
        "LODranges": "0, 20, 60, 100",
        "; cost": cost,
    })
    if not pd.isna(weapon["Dispersion Angle"]) and not weapon["Dispersion Angle"] == "":
        weapon_block["dispersion_angle"] = dfloat(weapon["Dispersion Angle"])
    
    # Create NPC blocks
    npc_ammo_nickname = weapon_block["projectile_archetype"][:3]+"npc_"+weapon_block["projectile_archetype"][3:]
    npc_weapon_nickname = nickname[:3]+"npc_"+nickname[3:]
    npc_hull_damage = hull_damage * dfloat(scaling_rules["NPC Damage Factor"])
    npc_energy_damage = energy_damage * dfloat(scaling_rules["NPC Damage Factor"])
    npc_power_usage = power_usage * dfloat(scaling_rules["NPC Energy Factor"])
    npc_effective_range = effective_range * dfloat(scaling_rules["NPC Range Factor"])
    npc_muzzle_velocity = muzzle_velocity * dfloat(scaling_rules["NPC Muzzle Velocity Factor"])
    npc_lifetime = npc_effective_range / npc_muzzle_velocity
    
    npc_munition_block = deepcopy(munition_block)
    npc_munition_block.update({"nickname": npc_ammo_nickname, "hull_damage": npc_hull_damage, "energy_damage": npc_energy_damage, "lifetime": npc_lifetime})
    npc_weapon_block = deepcopy(weapon_block)
    npc_weapon_block.update({"nickname": npc_weapon_nickname, "power_usage": npc_power_usage, "muzzle_velocity": npc_muzzle_velocity, "projectile_archetype": npc_ammo_nickname})
    
    return f"{nickname}_ammo", munition_block, npc_munition_block, nickname, weapon_block, npc_weapon_block

def create_auxgun_ammo_blocks(weapon: dict, variant: dict, scaling_rules: dict, idx: int, is_override: bool = False, make_ammo = False):
    
    # Hash out calculated values
    if not is_override or isinstance(weapon["Overrides"], float):
        hull_damage, energy_damage = dfloat(weapon["Hull DMG / rd"]), dfloat(weapon["Energy DMG / rd"])
            
        power_usage = (
                dfloat(weapon["Energy Usage / rd"]) *
                (1 + 0.01*dfloat(variant["Variant Energy Usage +%"]))
                )
        muzzle_velocity = dfloat(weapon["Muzzle Velocity"]) * (1 + 0.01*dfloat(variant["Variant Muzzle Velocity +%"]))
        effective_range = dfloat(weapon["Range"]) * (1 + 0.01*dfloat(variant["Variant Range +%"]))
        refire_rate = dfloat(weapon["Refire (rds / s)"]) * (1 + 0.01*dfloat(variant["Variant Refire Rate +%"])) # /s
        lifetime = dfloat(weapon["Range"]) / muzzle_velocity
        
        toughness = dfloat(weapon["Toughness Index"]) * dfloat(variant["Toughness Modifier"])
        cost = int(dfloat(weapon["Cost"]) * dfloat(variant["Cost Modifier"]))
    else:
        hull_damage, energy_damage = dfloat(weapon["Hull DMG / rd"]), dfloat(weapon["Energy DMG / rd"])
        power_usage = dfloat(weapon["Energy Usage / rd"])
        muzzle_velocity = dfloat(weapon["Muzzle Velocity"])
        effective_range = dfloat(weapon["Range"])
        refire_rate = dfloat(weapon["Refire (rds / s)"])
        lifetime = effective_range / muzzle_velocity
        
        toughness = dfloat(weapon["Toughness Index"])
        cost = int(dfloat(weapon["Cost"]))
    
    # HP Type won't be guessed for aux
    hp_type = HP_Types[weapon["HP Type"]] # FIXME turrets
    mt_name = "1x"
        
    # Get nickname from override or construct it
    if not is_override or isinstance(weapon["Overrides"], float):
        nickname = f"bm_{weapon['Family Shorthand']}_{weapon['Identifier']}_{mt_name}_{variant['Variant Shorthand']}"    
    else:
        nickname = weapon["Overrides"]
    
    # Create ammunition block
    if make_ammo is False:
        munition_block = None
    else:
        munition_block = OrderedDict({
            "nickname": f"{nickname}_ammo",
            "hp_type": "hp_gun", #TODO: Is this right?
            "requires_ammo": weapon["Uses Ammo?"],
            "ammo_limit": weapon["Ammo Limit"],
            "hit_pts": 2,
            "hull_damage": hull_damage,
            "energy_damage": energy_damage,
            "weapon_type": weapon["Weapon Type"],
            "one_shot_sound": f"{weapon['Fire Sound']}", # TODO: generate and use {variant['Variant Audio Shorthand']}
            "munition_hit_effect": weapon["Hit Effect"],
            "const_effect": f"{weapon['Projectile Effect']}", # TODO: generate and use {variant['Variant Visual Shorthand']}
            "lifetime": lifetime,
            "force_gun_ori": weapon["Force Gun Orientation"],
            "mass": 1
        })
        if str(weapon["Uses Ammo?"]).lower() == "true": #:vomit:
            munition_block["ids_name"] = idx+2
            munition_block["ids_info"] = idx+3
    
    # Create weapon block
    weapon_block = OrderedDict({
        "nickname": nickname,
        "ids_name": idx,
        "ids_info": idx+1,
        "DA_archetype": weapon["Gun Archetype"],
        "material_library": weapon["Material Library"],
        "HP_child": "HPConnect",
        "hit_pts": weapon["Gun HP"],
        "explosion_resistance": 0,
        "debris_type": "debris_normal",
        "parent_impulse": 20,
        "child_impulse": 80,
        "volume": 0,
        "mass": 10,
        "hp_gun_type": hp_type,
        "damage_per_fire": 0,
        "power_usage": power_usage,
        "refire_delay": 1. / refire_rate,
        "muzzle_velocity": muzzle_velocity,
        "use_animation": "Sc_fire",
        "toughness": toughness,
        "flash_particle_name": weapon["Flash Particle Name"],
        "flash_radius": 1,
        "light_anim": weapon["Light Animation"],
        "projectile_archetype": (f"{nickname}_ammo" if make_ammo is True else f"bm_{weapon['Family Shorthand']}_{weapon['Identifier']}_{mt_name}_b_ammo"),
        "separation_explosion": "sever_debris",
        "auto_turret": "false",
        "turn_rate": weapon["Turn Rate"],
        "lootable": "false",
        "LODranges": "0, 80, 160, 320, 400",
        "dry_fire_sound": "fire_dry",
        "; cost": cost,
    })
    if not pd.isna(weapon["Dispersion Angle"]) and not weapon["Dispersion Angle"] == "":
        weapon_block["dispersion_angle"] = dfloat(weapon["Dispersion Angle"])
    if not pd.isna(weapon["Muzzle Cone Override"]) and not weapon["Muzzle Cone Override"] == "":
        weapon_block["muzzle_cone_override"] = dfloat(weapon["Muzzle Cone Override"])
    if not pd.isna(weapon["Projectiles / shot"]) and not weapon["Projectiles / shot"] == "":
        weapon_block["total_projectiles_per_fire"] = dfloat(weapon["Projectiles / shot"])
    if not pd.isna(weapon["Burst Interval"]) and not weapon["Burst Interval"] == "":
        weapon_block["time_between_multiple_projectiles"] = dfloat(weapon["Burst Interval"])
    if not pd.isna(weapon["Free Ammo"]) and not weapon["Free Ammo"] == "":
        weapon_block["; free_ammo"] = dfloat(weapon["Free Ammo"])
    
    # Create NPC blocks
    npc_ammo_nickname = weapon_block["projectile_archetype"][:3]+"npc_"+weapon_block["projectile_archetype"][3:]
    npc_weapon_nickname = nickname[:3]+"npc_"+nickname[3:]
    npc_hull_damage = hull_damage * dfloat(scaling_rules["NPC Damage Factor"])
    npc_energy_damage = energy_damage * dfloat(scaling_rules["NPC Damage Factor"])
    npc_power_usage = power_usage * dfloat(scaling_rules["NPC Energy Factor"])
    npc_effective_range = effective_range * dfloat(scaling_rules["NPC Range Factor"])
    npc_muzzle_velocity = muzzle_velocity * dfloat(scaling_rules["NPC Muzzle Velocity Factor"])
    npc_lifetime = npc_effective_range / npc_muzzle_velocity
    
    npc_munition_block = deepcopy(munition_block)
    if make_ammo is True:
        npc_munition_block.update({"nickname": npc_ammo_nickname, "hull_damage": npc_hull_damage, "energy_damage": npc_energy_damage, "lifetime": npc_lifetime})
        if str(weapon["Uses Ammo?"]).lower() == "true": #:vomit:
            npc_munition_block.update({"ids_name": idx+6, "ids_info": idx+7})
    npc_weapon_block = deepcopy(weapon_block)
    npc_weapon_block.update({"nickname": npc_weapon_nickname, "power_usage": npc_power_usage, "muzzle_velocity": npc_muzzle_velocity, "projectile_archetype": npc_ammo_nickname, "auto_turret": "true"}) # npc aux guns HAVE to auto_turret, see https://github.com/better-modernized-combat/bmod-client/issues/35
    
    return f"{nickname}_ammo", munition_block, npc_munition_block, nickname, weapon_block, npc_weapon_block

def write_ammo_and_weapons(ini_out_file: str, ammo_dict: dict, weapon_dict: dict, npc_ammo_dict: dict, npc_weapon_dict: dict):
    
    with open(ini_out_file, "a", encoding = "utf-8") as out:
        
        for munition_name, munition_block in ammo_dict.items():
            out.write(f"[Munition]\n")
            for key, val in munition_block.items():
                if key.startswith(";"): # dont write "comments"
                    continue
                else:
                    if "\n" in str(val):
                        out.writelines([f"{key} = {sval}\n" for sval in val.split("\n")])
                    else:
                        out.writelines([f"{key} = {str(val)}\n"])
            out.write("\n")
        for weapon_name, weapon_block in weapon_dict.items():
            out.write(f"[Gun]\n")
            for key, val in weapon_block.items():
                if key.startswith(";"): # dont write "comments"
                    continue
                else:
                    if "\n" in str(val):
                        out.writelines([f"{key} = {sval}\n" for sval in val.split("\n")])
                    else:
                        out.writelines([f"{key} = {str(val)}\n"])
            out.write("\n")
            
        for munition_name, munition_block in npc_ammo_dict.items():
            out.write(f"[Munition]\n")
            for key, val in munition_block.items():
                if key.startswith(";"): # dont write "comments"
                    continue
                else:
                    if "\n" in str(val):
                        out.writelines([f"{key} = {sval}\n" for sval in val.split("\n")])
                    else:
                        out.writelines([f"{key} = {str(val)}\n"])
            out.write("\n")
        for weapon_name, weapon_block in npc_weapon_dict.items():
            out.write(f"[Gun]\n")
            for key, val in weapon_block.items():
                if key.startswith(";"): # dont write "comments"
                    continue
                else:
                    if "\n" in str(val):
                        out.writelines([f"{key} = {sval}\n" for sval in val.split("\n")])
                    else:
                        out.writelines([f"{key} = {str(val)}\n"])
            out.write("\n")

def create_blaster_good(blaster: dict, variant: dict, internal_name: str, ids_name: int, mp: int, is_turret: bool, is_override: bool = False):
    
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
        "price": (int(dfloat(blaster["Cost"]) * dfloat(variant["Cost Modifier"])) if not is_override else int(dfloat(blaster["Cost"]))),
        "item_icon": item_icon,
        "combinable": False,
        "ids_name": ids_name,
        "ids_info": ids_name+1,
        "shop_archetype": blaster["Gun Archetype"],
        "material_library": blaster["Material Library"],
        "DA_archetype": blaster["Gun Archetype"],
    })
    
    return good

def create_aux_good(auxgun: dict, variant: dict, internal_name: str, ids_name: int, is_override: bool = False):
    
    good = OrderedDict({
        "nickname": internal_name,
        "equipment": internal_name,
        "category": "equipment",
        "price": (int(dfloat(auxgun["Cost"]) * dfloat(variant["Cost Modifier"])) if not is_override else int(dfloat(auxgun["Cost"]))),
        "item_icon": auxgun["Item Icon"],
        "combinable": False,
        "ids_name": ids_name,
        "ids_info": ids_name+1,
        "shop_archetype": auxgun["Gun Archetype"],
        "material_library": auxgun["Material Library"],
        "DA_archetype": auxgun["Gun Archetype"],
    })
    
    if not(pd.isna(auxgun["Free Ammo"]) or auxgun["Free Ammo"] == ""):
        if is_override:
            print("WARNING: Guessing name of base variant for override aux gun that requires ammunition. If there is a crash right after this, its probably because your override aux gun didn't conform to the common naming scheme. If there is a crash when trying to buy this weapon, its for the same reason, as it can't find the ammo you're given for free.")
        base_variant_guess = "_".join(internal_name.split("_")[:-1]+["b"]) # FIXME: AUX Variants with Variant Ammo
        good["free_ammo"] = f"{base_variant_guess+'_ammo'}, {auxgun['Free Ammo']}"
    
    return good

def create_aux_ammo_good(auxgun: dict, internal_name: str, ids_name: int, is_override: bool = False):
    
    good = OrderedDict({
        "nickname": internal_name,
        "equipment": internal_name,
        "category": "equipment",
        "price": int(dfloat(auxgun["Ammo Cost"])), # FIXME: AUX Variants with Variant Ammo should have scaled costs, maybe
        "item_icon": auxgun["Ammo Icon"],
        "combinable": True,
        "ids_name": ids_name,
        "ids_info": ids_name+1,
        "shop_archetype": auxgun["Gun Archetype"],
        "material_library": auxgun["Material Library"]
    })
    
    return good

def write_goods(
    goods_out: str,
    goods: dict,
):
    with open(goods_out, "a") as out:
        
        for idx, good in goods.items():
            out.write("[Good]\n")
            for key, val in good.items():
                if "\n" in str(val):
                    out.writelines([f"{key} = {sval}\n" for sval in val.split("\n")])
                else:
                    out.writelines([f"{key} = {str(val)}\n"])
            out.write("\n\n")

def fill_admin_store(
    admin_store_location: str,
    admin_store_items: List[dict, ],
    filter: List = ["bm"] # by default literally allow in anything from bmod
):
    
    with open(admin_store_location, "r") as file:
        
        content = file.read()
        store_pattern = "(?<=;;; ADMIN STORE ;;;\n)((.|\n)*?)(?=;;; ADMIN STORE ;;;\n)"
        store = []
        # Add anything from any dict to the store by nickname that isnt npc gear
        for sublist in admin_store_items:
            store.extend([f"MarketGood = {nickname}, 0, -1, 10, 10, 0, 1" for nickname in sublist if not "npc" in nickname and any([x in nickname for x in filter])])
        replacement = "\n".join(store)+"\n"
        new_content = re.sub(store_pattern, replacement, content)
        
    with open(admin_store_location, "w") as file:
        
        file.write(new_content)

def sanity_check(
    weapons: dict, 
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
    for w1, w2 in tqdm(combinations(weapons, r = 2), total = int(len(weapons)*(len(weapons)-1)/2)):
        
        n1, n2 = weapons[w1]["nickname"], weapons[w2]["nickname"]
        
        # Skip aux, always
        if "aux" in n1 or "aux" in n2:
            continue
        
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
        
        hd1, hd2 = munitions[w1+"_ammo"]["hull_damage"], munitions[w2+"_ammo"]["hull_damage"]
        ed1, ed2 = munitions[w1+"_ammo"]["energy_damage"], munitions[w2+"_ammo"]["energy_damage"]
        mv1, mv2 = weapons[w1]["muzzle_velocity"], weapons[w2]["muzzle_velocity"]
        er1, er2 = mv1 * munitions[w1+"_ammo"]["lifetime"], mv2 * munitions[w2+"_ammo"]["lifetime"]
        rr1, rr2 = 1. / weapons[w1]["refire_delay"], 1. / weapons[w2]["refire_delay"]
        pu1, pu2 = weapons[w1]["power_usage"] / rr1, weapons[w2]["power_usage"] / rr2
        c1, c2 = weapons[w1]["; cost"], weapons[w2]["; cost"]
        hp1, hp2 = HP_Size[weapons[w1]["hp_gun_type"]], HP_Size[weapons[w2]["hp_gun_type"]]
        
        # Compare stats. If a stat is not required, set it to one of the other stats, so the result doesn't change.
        w1_eq_w2 = all([
            hd1 == hd2, 
            ed1 == ed2, 
            pu1 == pu2, 
            mv1 == mv2, 
            er1 == er2, 
            rr1 == rr2, 
            (hd1 == hd2 if include_cost is False else c1 == c2),
            (hd1 == hd2 if include_hardpoint_size is False else hp1 == hp2),
        ])
        if w1_eq_w2 is True:
            balancing_sane = False
            print(f"WARNING: Balance problem detected. Weapon {n1} is precisely equal to weapon {n2}.")
            continue
        w1_gt_w2 = all([
            hd1 >= hd2,
            ed1 >= ed2,
            pu1 <= pu2,
            mv1 >= mv2,
            er1 >= er2,
            rr1 >= rr2,
            (hd1 >= hd2 if include_cost is False else c1 <= c2),
            (hd1 >= hd2 if include_hardpoint_size is False else hp1 <= hp2),
        ])
        if w1_gt_w2 is True:
            balancing_sane = False
            print(f"WARNING: Balance problem detected. Weapon {n1} is strictly better than weapon {n2}.")
            print(f"{weapons[w1]['hp_gun_type']}, {weapons[w2]['hp_gun_type']}")
            continue
        w2_gt_w1 = all([
            hd2 >= hd1,
            ed2 >= ed1,
            pu2 <= pu1,
            mv2 >= mv1,
            er2 >= er1,
            rr2 >= rr1,
            (hd2 >= hd1 if include_cost is False else c2 <= c1),
            (hd2 >= hd1 if include_hardpoint_size is False else hp2 <= hp1),
        ])
        if w2_gt_w1 is True:
            balancing_sane = False
            print(f"WARNING: Balance problem detected. Weapon {n2} is strictly better than weapon {n1}.")
            print(f"{weapons[w1]['hp_gun_type']}, {weapons[w2]['hp_gun_type']}")
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

def create_guns(
    blaster_csv: str, 
    blaster_variant_csv: str, 
    blaster_scaling_rules_csv: str,
    aux_csv: str,
    aux_variant_csv: str,
    aux_scaling_rules_csv: str,
    weapon_out: str,
    weapon_goods_out: str,
    weapon_infocards_out: str,
    weapon_sanity_check: bool,
    ):
    
    # Create outfiles
    for file in [weapon_out, weapon_goods_out]:
        with open(file, "w") as out:
            for line in autogen_comment:
                out.write(line+"\n")
            out.write("\n")
    
    # Get CSVs
    try:
        blasters = pd.read_csv(blaster_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {blaster_csv} couldn't be read and is probably borked.")
    try:
        blaster_variants = pd.read_csv(blaster_variant_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object, keep_default_na = False)
    except:
        raise CSVError(f"CSV {blaster_variant_csv} couldn't be read and is probably borked.")
    try:
        blaster_scaling_rules_raw = pd.read_csv(blaster_scaling_rules_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {blaster_scaling_rules_csv} couldn't be read and is probably borked.")
    try:
        auxs = pd.read_csv(aux_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {aux_csv} couldn't be read and is probably borked.")
    try:
        aux_variants = pd.read_csv(aux_variant_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object, keep_default_na = False)
    except:
        raise CSVError(f"CSV {aux_variant_csv} couldn't be read and is probably borked.")
    try:
        aux_scaling_rules_raw = pd.read_csv(aux_scaling_rules_csv, sep = ",", encoding = "utf-8", comment = "#", dtype = object)
    except:
        raise CSVError(f"CSV {aux_scaling_rules_csv} couldn't be read and is probably borked.")

    # Clean out Unnamed cols, if any, those shouldn't be in the sheet
    blasters = clean_unnamed_wip_empty(blasters, name = blaster_csv)
    blaster_variants = clean_unnamed_wip_empty(blaster_variants, name = blaster_variant_csv)
    blaster_scaling_rules_raw = clean_unnamed_wip_empty(blaster_scaling_rules_raw, name = blaster_scaling_rules_csv)
    blaster_scaling_rules = make_scaling_rules(blaster_scaling_rules_raw)
    auxs = clean_unnamed_wip_empty(auxs, name = aux_csv)
    aux_variants = clean_unnamed_wip_empty(aux_variants, name = aux_variant_csv)
    aux_scaling_rules_raw = clean_unnamed_wip_empty(aux_scaling_rules_raw, name = aux_scaling_rules_csv)
    aux_scaling_rules = make_scaling_rules(aux_scaling_rules_raw)
    
    # Split off override entries
    is_override_blaster = blasters["Overrides"].apply(lambda x: False if pd.isna(x) or x == "" else True)
    base_blasters = blasters[~is_override_blaster]
    override_blasters = blasters[is_override_blaster]
    is_override_aux = auxs["Overrides"].apply(lambda x: False if pd.isna(x) or x == "" else True)
    base_auxs = auxs[~is_override_aux]
    override_auxs = auxs[is_override_aux]
    
    writable_munition_blocks = OrderedDict()
    writable_weapon_blocks = OrderedDict()
    writable_npc_munition_blocks = OrderedDict()
    writable_npc_weapon_blocks = OrderedDict()
    writable_infocards = OrderedDict()
    writable_goods = OrderedDict()
    
    # Iterate over all blasters/auxs and respective variants
    bd = base_blasters.to_dict(orient = "index").items()
    obd = override_blasters.to_dict(orient = "index").items()
    bvd = blaster_variants.to_dict(orient = "index").items()
    ad = base_auxs.to_dict(orient = "index").items()
    oad = override_auxs.to_dict(orient = "index").items()
    avd = aux_variants.to_dict(orient = "index").items()
    
    i_counter = ID_start
    
    for b, blaster in bd:
        
        for v, variant in bvd:
            
            # Save the base variant settings to use for overrides
            if v == 0:
                base_variant = deepcopy(variant)
            
            # Either generate all multiplicities (for S Energy weapons) or only the specific one specified
            for n, (multiplicity, is_turret) in enumerate(
                supported_multiplicities if blaster["HP Type"] == "S Energy" else
                [(3, True) if blaster["HP Type"] == "PD Turret" else (1, False)] # FIXME Turrets
                ):
                
                i_counter += 4 # weapon name, weapon info, npc weapon, npc weapon info
                
                munition_name, munition_block, npc_munition_block, weapon_name, weapon_block, npc_weapon_block = create_blaster_ammo_blocks(
                    weapon = blaster, 
                    variant = variant, 
                    multiplicity = multiplicity, 
                    scaling_rules = blaster_scaling_rules,
                    idx = i_counter,
                    is_turret = is_turret,
                    is_override = False,
                    )
                writable_munition_blocks[munition_name] = munition_block
                writable_weapon_blocks[weapon_name] = weapon_block
                writable_npc_munition_blocks[munition_name] = npc_munition_block
                writable_npc_weapon_blocks[weapon_name] = npc_weapon_block
                
                # Generate Infocard FRC entries
                display_name, formatted_infocard_content = generate_weapon_infocard_entry(
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
                writable_infocards[i_counter] = FRC_Entry(typus = "S", idx = i_counter, content = display_name)
                writable_infocards[i_counter+1] = FRC_Entry(typus = "H", idx = i_counter+1, content = formatted_infocard_content)
                writable_infocards[i_counter+2] = FRC_Entry(typus = "S", idx = i_counter+2, content = display_name)                 # NPC version
                writable_infocards[i_counter+3] = FRC_Entry(typus = "H", idx = i_counter+3, content = formatted_infocard_content)   # NPC version
                
                # Generate blaster goods entries
                writable_goods[weapon_block["nickname"]] = create_blaster_good(blaster = blaster, variant = variant, internal_name = weapon_block["nickname"], ids_name = i_counter, mp = multiplicity, is_turret = is_turret)
                writable_goods[npc_weapon_block["nickname"]] = create_blaster_good(blaster = blaster, variant = variant, internal_name = npc_weapon_block["nickname"], ids_name = i_counter+2, mp = multiplicity, is_turret = is_turret) # NPC version
                
    for o, override_blaster in obd:
        
        # Figure out what the override weapon should be doing
        nickname = override_blaster["Overrides"]
        split = nickname.split("_")
        mt_name = split[-2]
        
        # Get the variant that is being overwritten (for infocard snips), assuming base if its a new custom gun
        if nickname in writable_weapon_blocks:
            _, variant = next(iter(blaster_variants[blaster_variants["Variant Shorthand"] == split[-1]].to_dict(orient = "index").items()))
        else:
            variant = base_variant
        multiplicity = int(mt_name[0])
        is_turret = (override_blaster["HP Type"] == "PD Turret" or mt_name[-1] == "T")
        
        i_counter += 2 # weapon name, weapon info
        
        munition_name, munition_block, npc_munition_block, weapon_name, weapon_block, npc_weapon_block = create_blaster_ammo_blocks(
            weapon = override_blaster, 
            variant = variant,
            multiplicity = multiplicity,
            scaling_rules = blaster_scaling_rules,
            idx = i_counter,
            is_turret = is_turret, # FIXME turrets
            is_override = True
            )
        if "_npc_" in override_blaster["Overrides"]:
            writable_npc_munition_blocks[munition_name] = npc_munition_block
            writable_npc_weapon_blocks[weapon_name] = npc_weapon_block
        else:
            writable_munition_blocks[munition_name] = munition_block
            writable_weapon_blocks[weapon_name] = weapon_block
        
        # Generate Infocard FRC entries
        display_name, formatted_infocard_content = generate_weapon_infocard_entry(
            name = override_blaster["Weapon Name"],
            long_name = override_blaster["Long Name"],
            info = override_blaster["Base Infocard"],
            is_turret = is_turret,
            mp = multiplicity,
            mp_info = infocard_boilerplate[(multiplicity, is_turret)],
            variant_sh = variant["Variant Shorthand"],
            variant_desc = variant["Variant Description"],
            variant_info = variant["Variant Infocard Paragraph"],
            variant_display = variant["Display Name Suffix"],
        )
        writable_infocards[i_counter] = FRC_Entry(typus = "S", idx = i_counter, content = display_name)
        writable_infocards[i_counter+1] = FRC_Entry(typus = "H", idx = i_counter+1, content = formatted_infocard_content)
        
        # Generate blaster goods entries
        writable_goods[weapon_block["nickname"]] = create_blaster_good(blaster = override_blaster, variant = variant, internal_name = weapon_block["nickname"], ids_name = i_counter, mp = multiplicity, is_turret = is_turret)

    for a, aux, in ad:
        
        for v, variant in avd:
        
            # Save the base variant settings to use for overrides
            if v == 0:
                base_variant = deepcopy(variant)
            
            i_counter += 8 # weapon name, weapon info, ammo name, ammo info, npc equivalents
            
            munition_name, munition_block, npc_munition_block, weapon_name, weapon_block, npc_weapon_block = create_auxgun_ammo_blocks(
                weapon = aux, 
                variant = variant,
                scaling_rules = aux_scaling_rules,
                idx = i_counter,
                is_override = False,
                make_ammo = (v == 0)
                )
            if v == 0: # see https://github.com/better-modernized-combat/bmod-client/issues/23#issuecomment-1934895042
                writable_munition_blocks[munition_name] = munition_block
                base_munition_name = munition_name
            writable_weapon_blocks[weapon_name] = weapon_block
            if v == 0: # see above
                writable_npc_munition_blocks[munition_name] = npc_munition_block
                base_npc_munition_name = npc_munition_block["nickname"]
            writable_npc_weapon_blocks[weapon_name] = npc_weapon_block
            
            # Generate Weapon Infocard FRC entries
            display_name, formatted_infocard_content = generate_weapon_infocard_entry(
                name = aux["Weapon Name"],
                long_name = aux["Long Name"],
                info = aux["Base Infocard"],
                is_turret = False,
                mp = 1,
                mp_info = infocard_boilerplate[(1, False)],
                variant_sh = variant["Variant Shorthand"],
                variant_desc = variant["Variant Description"],
                variant_info = variant["Variant Infocard Paragraph"],
                variant_display = variant["Display Name Suffix"],
            )
            if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit:
                ammo_name, ammo_infocard_content = generate_ammo_infocard_entry(
                    name = aux["Ammo Name"],
                    info = aux["Ammo Infocard"],
                )
            # Generate Ammo Infocard FRC entries
            writable_infocards[i_counter] = FRC_Entry(typus = "S", idx = i_counter, content = display_name)
            writable_infocards[i_counter+1] = FRC_Entry(typus = "H", idx = i_counter+1, content = formatted_infocard_content)
            if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit:
                writable_infocards[i_counter+2] = FRC_Entry(typus = "S", idx = i_counter+2, content = ammo_name)
                writable_infocards[i_counter+3] = FRC_Entry(typus = "H", idx = i_counter+3, content = ammo_infocard_content)
            
            writable_infocards[i_counter+4] = FRC_Entry(typus = "S", idx = i_counter+4, content = display_name)                 # NPC version
            writable_infocards[i_counter+5] = FRC_Entry(typus = "H", idx = i_counter+5, content = formatted_infocard_content)   # NPC version
            if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit:
                writable_infocards[i_counter+6] = FRC_Entry(typus = "S", idx = i_counter+6, content = ammo_name)                # NPC version
                writable_infocards[i_counter+7] = FRC_Entry(typus = "H", idx = i_counter+7, content = ammo_infocard_content)    # NPC version
                
            # Generate auxgun goods entries
            writable_goods[weapon_block["nickname"]] = create_aux_good(auxgun = aux, variant = variant, internal_name = weapon_block["nickname"], ids_name = i_counter)
            writable_goods[npc_weapon_block["nickname"]] = create_aux_good(auxgun = aux, variant = variant, internal_name = npc_weapon_block["nickname"], ids_name = i_counter+4) # NPC version
            
            # Generate ammo goods entries if weapon requires ammo
            if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit:
                writable_goods[base_munition_name] = create_aux_ammo_good(auxgun = aux, internal_name = base_munition_name, ids_name = i_counter+2)
                writable_goods[base_npc_munition_name] = create_aux_ammo_good(auxgun = aux, internal_name = base_npc_munition_name, ids_name = i_counter+6) # NPC version
        
    for o, override_aux in oad:
        
        # Figure out what the override weapon should be doing
        nickname = override_aux["Overrides"]
        
        # Get the variant that is being overwritten (for infocard snips), assuming base if its a new custom gun
        if nickname in writable_weapon_blocks:
            _, variant = next(iter(blaster_variants[blaster_variants["Variant Shorthand"] == split[-1]].to_dict(orient = "index").items()))
        else:
            variant = base_variant
        multiplicity = 1
        is_turret = False
        
        i_counter += 4 # weapon name, weapon info, ammo name, ammo info
        
        munition_name, munition_block, npc_munition_block, weapon_name, weapon_block, npc_weapon_block = create_auxgun_ammo_blocks(
            weapon = override_aux, 
            variant = variant,
            scaling_rules = aux_scaling_rules,
            idx = i_counter,
            is_override = True,
            make_ammo = True
            )
        if "_npc_" in override_aux["Overrides"]:
            writable_npc_munition_blocks[munition_name] = npc_munition_block
            writable_npc_weapon_blocks[weapon_name] = npc_weapon_block
        else:
            writable_munition_blocks[munition_name] = munition_block
            writable_weapon_blocks[weapon_name] = weapon_block
        
        # Generate Infocard FRC entries
        display_name, formatted_infocard_content = generate_weapon_infocard_entry(
            name = override_aux["Weapon Name"],
            long_name = override_aux["Long Name"],
            info = override_aux["Base Infocard"],
            is_turret = False,
            mp = 1,
            mp_info = infocard_boilerplate[(1, False)],
            variant_sh = variant["Variant Shorthand"],
            variant_desc = variant["Variant Description"],
            variant_info = variant["Variant Infocard Paragraph"],
            variant_display = variant["Display Name Suffix"],
        )
        if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit::
            ammo_name, ammo_infocard_content = generate_ammo_infocard_entry(
                name = aux["Ammo Name"],
                info = aux["Ammo Infocard"],
            )
        writable_infocards[i_counter] = FRC_Entry(typus = "S", idx = i_counter, content = display_name)
        writable_infocards[i_counter+1] = FRC_Entry(typus = "H", idx = i_counter+1, content = formatted_infocard_content)
        if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit:
            writable_infocards[i_counter+2] = FRC_Entry(typus = "S", idx = i_counter+2, content = display_name)
            writable_infocards[i_counter+3] = FRC_Entry(typus = "H", idx = i_counter+3, content = formatted_infocard_content)
            
        # Generate auxgun goods entries
        writable_goods[weapon_block["nickname"]] = create_aux_good(auxgun = override_aux, variant = variant, internal_name = weapon_block["nickname"], ids_name = i_counter, is_override = True)
        
        # Do not generate ammo goods entries if weapon requires ammo - we STILL use the base variant here
        #if str(aux["Uses Ammo?"]).lower() == "true" and v == 0: #:vomit:
        #    writable_goods[weapon_block["nickname"]] = create_aux_ammo_good(auxgun = override_aux, internal_name = ????, ids_name = i_counter+2, is_override = True)
        
    # Sanity check weapon balance. NPC weapon balance is implied by PC weapon balance (probably), sorta irrelevant, and therefore ignored.
    if weapon_sanity_check is True:
        sanity_check(writable_weapon_blocks, writable_munition_blocks)
    
    # Write to inis/frc.
    write_ammo_and_weapons(weapon_out, writable_munition_blocks, writable_weapon_blocks, writable_npc_munition_blocks, writable_npc_weapon_blocks)
    write_infocards_to_frc(weapon_infocards_out, writable_infocards)
    write_goods(weapon_goods_out, writable_goods)
    
    # Fill admin store with goodies (for testing)
    fill_admin_store(
        admin_store_location = "mod-assets\\DATA\\BMOD\\EQUIPMENT\\bmod_market_misc.ini",
        admin_store_items = [
            [munition_name for munition_name, munition in writable_munition_blocks.items() if "aux" in munition_name and str(munition["requires_ammo"]).lower() == "true"], 
            writable_weapon_blocks
            ],
        filter = ["1x_b", "3x_b", "2x_b"]
        )
    
    # TODO: generate the following corresponding files based on the name of the gun:
    ### - flash_particle_name, const_effect, munition_hit_effect, one_shot_sound
    # TODO: fix variant and override weapon costs

if __name__ == "__main__":
    
    parser = ArgumentParser()
    parser.add_argument("--blaster_csv", dest = "blaster_csv", type = str)
    parser.add_argument("--blaster_variant_csv", dest = "blaster_variant_csv", type = str)
    parser.add_argument("--blaster_scaling_rules_csv", dest = "blaster_scaling_rules_csv", type = str)
    parser.add_argument("--aux_csv", dest = "aux_csv", type = str)
    parser.add_argument("--aux_variant_csv", dest = "aux_variant_csv", type = str)
    parser.add_argument("--aux_scaling_rules_csv", dest = "aux_scaling_rules_csv", type = str)
    parser.add_argument("--weapon_out", dest = "weapon_out", type = str)
    parser.add_argument("--weapon_goods_out", dest = "weapon_goods_out", type = str)
    parser.add_argument("--weapon_infocards_out", dest = "weapon_infocards_out", type = str)
    parser.add_argument("--weapon_sanity_check", dest = "weapon_sanity_check", action = "store_true", default = False)
    
    args = parser.parse_args()
    
    create_guns(
        blaster_csv = args.blaster_csv,
        blaster_variant_csv = args.blaster_variant_csv,
        blaster_scaling_rules_csv = args.blaster_scaling_rules_csv,
        aux_csv = args.aux_csv,
        aux_variant_csv = args.aux_variant_csv,
        aux_scaling_rules_csv = args.aux_scaling_rules_csv,
        weapon_out = args.weapon_out,
        weapon_goods_out = args.weapon_goods_out,
        weapon_infocards_out = args.weapon_infocards_out,
        weapon_sanity_check = args.weapon_sanity_check,
        )