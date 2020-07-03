# -*- coding: utf-8 -*-

import os
import re
from opencc import OpenCC


def func(path):
    path = path.replace("\\", "/").strip("'").strip('"').strip("/")
    names = os.listdir(path)
    plainText = [x for x in names if x[-3:].lower() in ("lrc", "ass", "txt", "ssa", "srt")]
    for a in plainText:
        pt = f"{path}/{a}"
        with open(pt, encoding="utf-8") as f:
            data = cc.convert(f.read())
        with open(pt, mode="w+", encoding="utf-8") as f:
            f.write(data)
    print("done.")

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
