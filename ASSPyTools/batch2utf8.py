# -*- coding: utf-8 -*-
# The first script I edit in 2020-02-17

import os
from chardet import detect


def e2utf8(path):
    path = path.replace("\\", "/").strip("'").strip('"').strip("/")
    names = os.listdir(path)
    plainText = [
        x for x in names if x[-3:].lower() in ("lrc", "ass", "txt", "ssa", "srt")
    ]
    for a in plainText:
        pt = f"{path}/{a}"
        with open(pt, "rb+") as fp:
            content = fp.read()
            codeType = detect(content)["encoding"]
            if codeType == "GB2312":
                codeType = "GBK"
            # chardet 踩坑：GBK 是 GB2312 的超集，当字符在 GBK 集合中，但不在 GB2312 时，就会乱码。
            # 因此当 chardet.detect 识别出 GB2312 时，直接用 GBK，CP936? 或者 GB18030 decode 即可。
            elif codeType == "utf-8":
                print(a, ": No need.")
                continue
            content = content.decode(codeType, "ignore").encode("utf-8")
            fp.seek(0)
        with open(pt, "wb+") as f:
            f.write(content)
        print(a, ": Finished.")
    x = os.system("echo Press any key to continue... & pause > nul")


if __name__ == "__main__":
    path = input("Input dir you wanna batch process:")
    e2utf8(path)
