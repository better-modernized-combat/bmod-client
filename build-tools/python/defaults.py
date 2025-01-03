autogen_comment = [
    ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
    ";; THIS FILE HAS BEEN AUTOMATICALLY GENERATED. ;;",
    ";;        PLEASE DO NOT EDIT THIS FILE.        ;;",
    ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
]

legacy_comment = [
    ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
    ";;  THIS CONTENT IS LEGACY CONTENT AND SHOULD  ;;",
    ";;          BE CONSIDERED DEPRECATED.          ;;",
    ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
]

sep = [
    ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
    ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;",
]

# Missiles intentionally not included
HP_Types = {
    "S Energy": "hp_gun_special_1",
    "M Energy": "hp_gun_special_2",
    "L Energy": "hp_gun_special_3",
    #"S Missile": "hp_gun_special_4",
    #"M Missile": "hp_gun_special_5",
    #"L Missile": "hp_gun_special_6",
    "S Ballistic": "hp_gun_special_7",
    "M Ballistic": "hp_gun_special_8",
    "L Ballistic": "hp_gun_special_9",
    #"Something": "hp_gun_special_10"
    "S Fleet Energy": "hp_turret_special_1",
    "M Fleet Energy": "hp_turret_special_2",
    "L Fleet Energy": "hp_turret_special_3",
    "S Fleet Missile": "hp_turret_special_4",
    "M Fleet Missile": "hp_turret_special_5",
    "L Fleet Missile": "hp_turret_special_6",
    "S Fleet Ballistic": "hp_turret_special_7",
    "M Fleet Ballistic": "hp_turret_special_8",
    "L Fleet Ballistic": "hp_turret_special_9",
    #"XL Missile": "hp_turret_special_4",
    "PD Turret": "hp_turret_special_10",
    "XL Support": "hp_freighter_shield_special_10",
}

HP_Size = {
    "hp_gun_special_1": 1,
    "hp_gun_special_2": 2,
    "hp_gun_special_3": 3,
    "hp_gun_special_4": 1,
    "hp_gun_special_5": 1,
    "hp_gun_special_6": 1,
    "hp_gun_special_7": 1,
    "hp_gun_special_8": 1,
    "hp_gun_special_9": 1,
    #"hp_gun_special_10": 1,
    "hp_turret_special_1": 1,
    "hp_turret_special_2": 1,
    "hp_turret_special_3": 1,
    "hp_turret_special_4": 1,
    "hp_turret_special_5": 1,
    "hp_turret_special_6": 1,
    "hp_turret_special_7": 1,
    "hp_turret_special_8": 1,
    "hp_turret_special_9": 1,
    "hp_turret_special_10": 1,
    "hp_freighter_shield_special_10": 1,
}

infocard_boilerplate = {
    (1, False): "",
    (2, False): "This twin-linked housing combines two <BLASTER_NAME> blasters into a single fixture, requiring a Medium Energy hardpoint to mount. Twin-linked blasters pack double the power into every shot, but are slightly less energy efficient and accurate than their smaller cousins.",
    (3, False): "This tri-linked housing combines three <BLASTER_NAME> blasters into a single fixture, requiring a Large Energy hardpoint to mount. Tri-linked blasters pack triple the power into every shot, but are somewhat less energy efficient and accurate than their smaller cousins.",
    #(3, True): "This tri-linked housing pairs three <BLASTER_NAME> blasters and a gimballed turret mount, requiring a specialized PD hardpoint to mount.",
    (1, "aux"): "This weapon is an AUX weapon which requires a specialized hardpoint to mount.",
}

infocard_multiplicity = {
    (1, False): "",
    (2, False): " Twin-Linked",
    (3, False): " Tri-Linked",
    #(3, True): " Tri-Linked Gyromounted",
    (1, "aux"): "",
}

display_multiplicity = {
    (1, False): "",
    (2, False): " 2x",
    (3, False): " 3x",
    #(3, True): " 3x Turret",
    (1, "aux"): "",
}

ID_start = 534465 # TODO