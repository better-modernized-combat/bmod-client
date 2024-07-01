from defaults import *

"""
Infocard numbers for variant weapons are/should be generated as follows:
1) Start at 600001. This is the first base weapon's S entry (e.g. "S 600001 Scorpion").
2) Every new base_weapon jumps ahead 400 entries. (e.g. "S 600401 Tarantula".)
3) The H entry lives next to it (e.g. "H 600002 \m\\bM1-D "Scorpion" Xenos Particle Cannon\n\nThe M1-D Scorpion is a really cool gun, which features ...")
4) The corresponding S and H entry for NPC blasters come right after. They generally look the same, unless explicitly specified as different.

Currently, infocards and variants are NOT generated for aux/missile weaponry. Correspondingly, those infocards and names still live in the original file.
"""

class FRC_Entry:
    
    def __init__(self, typus: str, idx: int, content: str):
        self.typus = typus
        self.idx = idx
        self.content = content

def write_infocards_to_frc(
    infocards_out: str,
    infocards: dict,
):
    
    with open(infocards_out, "w", encoding = "utf-16") as out:
        
        out.write(f"S {ID_start-1} File Starts Here\n")
        #out.write("S 600000 File Starts Here\n")
        
        for idx, entry in infocards.items():
            if entry.typus == "S":
                out.write(f"S {idx} {entry.content}\n")
            elif entry.typus == "H":
                out.write(f"H {idx}\n{entry.content}\n")
            else:
                raise NotImplementedError(f"Unknown FRC entry type {entry.typus} for entry {entry.idx}. Known types are 'S', 'H'.")

def generate_weapon_infocard_entry(
    name: str,              # Display name of the gun (i.e. "Scorpion")
    long_name: str,         # Long name of the gun (i.e. M1-D "Scorpion" Xenos Particle Cannon)
    info: str,              # Infocard text, without header
    is_turret: bool,        # Is Turret?
    mp: int,                # Multiplicity ((1, False) for 1x, non-turret, (2, False) for 2x, non-turret, etc.
    mp_info: str,           # Multiplicity flavor text ("This Tri-Linked blaster bla bla bla ...")
    variant_sh: str,        # Variant Shorthand (b for base, xdm for increased damage, etc)
    variant_desc: str,      # Variant Description (e.g. " - Increased Damage" for xdm weapons)
    variant_info: str,      # Variant Info (e.g. "This particular piece of equipment deals increased damage at the cost ...")
    variant_display: str    # Variant Display Suffix (e.g. "Scorpion" becomes "Scorpion [+]")
    ):
    
    try:
    
        display_name = name+display_multiplicity[(mp, is_turret)]+variant_display
        
        info_paragraphs = info.split("\n\n")
        
        new_info = []
        new_info.append(info_paragraphs[0])
        if mp_info:
            mp_info = mp_info.replace("<BLASTER_NAME>", name)
            new_info.append(mp_info)
        if variant_info:
            new_info.append(variant_info)
        if len(info_paragraphs) > 1:
            new_info.extend(info_paragraphs[1:])
        new_info = "\n\t\n\t".join(new_info)
            
        long_name_split = long_name.split(" ")
        long_name_num = long_name_split[0]
        s1 = " " if infocard_multiplicity[(mp, is_turret)] else ""
        vsh = "-"+variant_sh.upper() if variant_sh not in ["b", "xpq"] else ""
        infocard_header = f'\\m\\b{infocard_multiplicity[(mp, is_turret)]}{s1}{long_name_num}{vsh} {" ".join(long_name_split[1:])}{variant_desc}\\B'
        
        new_infocard = f'\t{infocard_header}\n\t\\l\n\t{new_info}\\n\n\t'
        
        return display_name, new_infocard
    
    except:
        
        print(f"ERROR: Could not generate variant Infocard entry for {name}. Maybe the format is different from the regular format for this type of weapon?")
        return display_name, info

def generate_ammo_infocard_entry(
    name: str,                  # Display name of the gun (i.e. "Scorpion")
    info: str,                  # Infocard text, without header
    variant_desc: str = "",     # Variant Description (e.g. " - Increased Damage" for xdm weapons)
    variant_display: str = ""   # Variant Display Suffix (e.g. "Scorpion" becomes "Scorpion [+]")
    ):
    
    display_name = name+variant_display
    infocard_header = f'\\m\\b{name}{variant_desc}\\B'
    infocard = f'\t{infocard_header}\n\t\\l\n\t{info}\\n\n\t'
    
    return display_name, infocard