# -*- coding: utf-8 -*-
# The first python script I wrote in 2020-02-16-02:22

import os
import re


def func(path):
    path = path.replace("\\", "/").strip("'").strip('"').strip("/")
    names = os.listdir(path)
    namesL = [x.lower() for x in names]
    n = 0
    for i, name in enumerate(namesL):
        if name[-3:] != "ass":
            continue
        for ext in ("mp4", "mkv", "wmv", "avi"):
            if f"{name[:-4]}.{ext}" in namesL:
                n += 1
                assPath = f"{path}/{name}"
                with open(assPath, encoding="UTF-8") as f:
                    data = f.read()
                    data = re.sub(
                        r"((?<=\n(Audio|Video)\sFile:)|(?<=\nTitle:)).*?\n",
                        f" {names[i]}\n",
                        data,
                        3,
                    )
                with open(assPath, mode="w", encoding="UTF-8") as f:
                    f.write(data)
    print(f"Found {n} pair(s) matching the video. Finished.")


if __name__ == "__main__":
    path = input("Input dir you wanna batch edit:")
    func(path)

