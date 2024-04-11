import time
from typing import List

def parse_blocks(in_file: str) -> dict:

    with open(in_file, "r") as o:
        lines = o.readlines()

    blocks = {}
    nicknames = {}
    start_lines = []
    i = 0

    for line in lines:

        if line.startswith("["):
            i += 1
            blocks[i] = {}
            blocks[i]["type"] = line.strip()
            blocks[i]["content"] = []
            blocks[i]["dependencies"] = []
        elif line.startswith("nickname ="):
            nickname = line.split(" = ")[1].strip()
            blocks[i]["nickname"] = nickname
            nicknames[nickname] = i
        elif i==0:
            start_lines.append(line.strip())
        else:
            if "=" in line:
                vals = line.split(" = ")[1]
                for val in vals.split(","):
                    val = val.strip()
                    if val in nicknames:
                        blocks[i]["dependencies"].append(nicknames[val])
            elif line.strip() == "":
                continue
            blocks[i]["content"].append(line.strip())

    return start_lines, lines, blocks, nicknames


def resolve_dependencies(blocks: dict, i: int):
    
    # get dependencies
    dep = blocks[i]["dependencies"]
        
    # if empty, return (or if depending on itself, which can happen if theres something with the same name but outside the file thats referenced - effectively, this is ignored)
    if dep == [] or dep == [i]:
        return [i]
    # if sub-dependencies, resolve each, prepending current
    else:
        r = [i]
        for d in dep:
            r.extend(resolve_dependencies(blocks, d))
        return r


def sort_blocks_by_indices(blocks: dict, order_by_type: List[str, ]) -> List[int, ]:
    
    order = []
    # for every object type, starting with the one highest in the typical hierarchy
    for t in order_by_type:
        # go over each block
        for i, block in blocks.items():
            # object of right type
            if block["type"] == t:
                # get all dependencies, which are ordered top to bottom
                rd = resolve_dependencies(blocks, i)
                # starting from the bottom, add all dependencies
                for d in rd[::-1]:
                    order.append(d)

    # return an ordered set of the collected dependencies
    return list({d: None for d in order}.keys())


def blocks_to_lines(blocks: dict, order: List[int, ], start_lines: List[str, ]) -> List[str, ]:
    
    out_lines = [s+"\n" for s in start_lines]
    for i in order:
        b = blocks[i]
        out_lines.append(b["type"]+"\n")
        out_lines.append("nickname = "+b["nickname"]+"\n")
        out_lines.extend([l+"\n" for l in b["content"]])
        out_lines.append("\n")

    return out_lines


def test_integrity(a: List, b: List) -> None:

    print(len(a), len(b))
    assert sorted(a) == sorted(b)


def sort_ini(in_file: str, out_file: str, order_by_type: List[str, ]):

    s, l, b, n = parse_blocks(in_file)
    #print(b[len(b)], b[1])
    o = sort_blocks_by_indices(b, order_by_type)
    #print(o)
    w = blocks_to_lines(b, o, s)
    #print(w)
    #test_integrity(l, w)
    with open(out_file, "w") as o:
        for line in w:
            o.write(line)


if __name__ == "__main__":

    ts = time.time()
    #in_file = "./mod-assets/DATA/BMOD/EQUIPMENT/bmod_equip_guns.ini"
    #in_file = "./mod-assets/DATA/BMOD/EQUIPMENT/bmod_equip_amssle.ini"
    in_file = "./mod-assets/DATA/BMOD/EQUIPMENT/bmod_equip_solar.ini"
    out_file = in_file.replace(".ini", "_sorted.ini")
    sort_ini(
        in_file = in_file,
        out_file = out_file,
        #order_by_type = ["[Gun]", "[Munition]"]
        order_by_type = ["[Gun]", "[Munition]", "[Motor]", "[Explosion]"]
        )
    te = time.time()
    print(te - ts)