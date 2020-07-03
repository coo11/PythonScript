# -*- coding: utf-8 -*-
# The second script I wrote in 2020-02-17
# package name: opencc-python-reimplemented

import os
import re
from opencc import OpenCC


def func(path):
    path = path.replace("\\", "/").strip("'").strip('"').strip("/")
    names = os.listdir(path)
    ass = [x for x in names if x[-3:].lower() == 'ass']
    for a in ass:
        assFile = f"{path}/{a}"
        with open(assFile, encoding="utf-8") as f:
            data = f.read()
            part1, part2, part3 = re.split(r"(?<=styles\]\n|events\]\n)", data, 2, re.I)
            regex = getPropertyRegex(part2, "name", "style")
            jp = [
                b.strip(" ")
                for b in regex.findall(part2)
                if re.search("(?i:jp|japan)", b)
            ]
            print(a, ': ', ', '.join(jp), 'excluded.')  # Display all style might be excluded because of Japanese
            regex = getPropertyRegex(part3, "style", "dialogue")

            def repl(obj):
                if obj.group(1).strip(" ") in jp:
                    return obj.group(0)
                else:
                    return cc.convert(obj.group(0))

            part3 = re.sub(regex, repl, part3)
        with open(assFile, mode="w+", encoding="utf-8") as f:
            f.write(f"{part1}{part2}{part3}")
    print("done.")


def getPropertyRegex(string, str, prefix):
    formatLineList = re.split(
        r"\W+", re.match(r"Format:(.*?)\n", string, re.I).group(1).lower().strip(" ")
    )
    r = formatLineList.index(str)
    if r + 1 != len(formatLineList):
        regex = re.compile(rf"{prefix}:(.*?,){{{r + 1}}}.*?\n", re.I)
    else:
        regex = re.compile(rf"{prefix}:(?:.*?,){{{r}}}(.*?\n)", re.I)
    return regex


if __name__ == "__main__":
    cc = OpenCC("t2s")
    type = (
        "t2s",
        "t2hk",
        "t2tw",
        "tw2s",
        "tw2sp",
        "hk2s",
        "s2hk",
        "s2t",
        "s2tw",
        "s2twp",
    )
    items = "\n".join([f"{x[0]}. {x[1]}" for x in enumerate(type)])
    n = input(
        f'WARNING: JAPANESE CHARACTER maybe affected!\n{items}\nInput number to select a convert type.\nInput nothing and enter to use "t2s" by default:'
    )
    try:
        if n != "":
            cc.set_conversion(int(n))
    except ValueError:
        print("Cancelled")
    else:
        path = input("Input dir you wanna batch edit:")
        func(path)
