import os
from tqdm.auto import tqdm
from typing import List

# Find all freelancer inis
def recursive_find(top: str, ftype: str = ".ini", level: int = 0):

    out = []
    ld = [os.path.join(os.path.abspath(top), item) for item in os.listdir(top)]
    filenames = [f for f in ld if os.path.isfile(f) and f.endswith(ftype)]
    dirnames = [d for d in ld if os.path.isdir(d)]
    out.extend(filenames)
    for dirname in dirnames:
        out.extend(recursive_find(top = dirname, ftype = ftype, level = level+1))
    return out

# Replace across file
def find_and_replace(lines: List[str, ], old: str, new: str, strict: bool = True):
    
    new_lines = []
    for line in lines:
        if strict is True:
            if not "=" in line:
                new_lines.append(line)
                continue
            split = line.split(" = ")
            key, value = split[0], split[1].strip("\r\n")
            if value == old:
                new_lines.append(f"{key} = {new}\n")
            else:
                new_lines.append(line)
        else:
            if old in line:
                new_lines.append(line.replace(old, new))
            else:
                new_lines.append(line)
    return new_lines    

if __name__ == "__main__":
    
    print("Remember that blindly replacing strings with other strings can have unintended consequences and that I hope you suffer them :v)")
    
    fl_install_path = input("Enter your FL path (mod build area, not FL install): ")
    inis = recursive_find(fl_install_path)
    old = input("String to replace: ")
    new = input("Replacement string: ")
    
    for ini in tqdm(inis):
        with open(ini, "r", encoding = "utf-8") as o:
            lines = o.readlines()
        with open(ini, "w", encoding = "utf-8") as o:
            o.writelines(find_and_replace(lines = lines, old = old, new = new, strict = True))