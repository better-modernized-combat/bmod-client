HP_Types = {
    "S Energy": "hp_gun_special_1",
    "M Energy": "hp_gun_special_2",
    "L Energy": "hp_gun_special_3",
    "L Energy Turret": "hp_turret_special_9" 
}

HP_Size = {
    "hp_gun_special_1": 1,
    "hp_gun_special_2": 2,
    "hp_gun_special_3": 3,
    "hp_turret_special_9": 3
}

infocard_boilerplate = {
    (1, False): "",
    (2, False): "This twin-linked housing combines two <BLASTER_NAME> blasters into a single fixture, requiring a Medium Energy hardpoint to mount. Twin-linked blasters pack double the power into every shot, but are slightly less energy efficient and accurate than their smaller cousins.",
    (3, False): "This tri-linked housing combines three <BLASTER_NAME> blasters into a single fixture, requiring a Large Energy hardpoint to mount. Tri-linked blasters pack triple the power into every shot, but are somewhat less energy efficient and accurate than their smaller cousins.",
    (3, True): "This tri-linked housing pairs three <BLASTER_NAME> blasters and a gimballed turret mount, requiring a specialized PD hardpoint to mount."
}

infocard_multiplicity = {
    (1, False): "",
    (2, False): " Twin-Linked",
    (3, False): " Tri-Linked",
    (3, True): " Tri-Linked Gyromounted",
}

display_multiplicity = {
    (1, False): "",
    (2, False): " 2x",
    (3, False): " 3x",
    (3, True): " 3x Turret",
}