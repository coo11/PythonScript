# -*- coding: utf-8 -*-
from PIL import Image
from time import time
import os, math


class Stitcher:
    """A tool to stitch images in one"""

    def __init__(
        self,
        *,
        spacing=20,
        isZigzag=True,
        isVertical=False,
        isRightToLeft=False,
        keep="size",
        verticalAlign="top",
        horizontalAlign="left",
        oneline=True,
        sortBy="name",
        sortAscending=True,
        bgColor="#333",
        saveFormat="",
        saveName="",
        saveDir=os.path.join(os.environ["USERPROFILE"], "Desktop"),
        saveOptions={"quality": 95, "optimize": True},
    ):
        self.inputPath()
        self.getSortedImagesInfo()
        self.sortImages(sortBy, not sortAscending)
        self.inputRowOrColumn()
        self.keep = keep
        self.setLayoutDetails(isZigzag, isVertical, isRightToLeft)
        self.drawOnCanvas(spacing, bgColor, verticalAlign, horizontalAlign)
        self.save(saveFormat, saveName, saveDir, **saveOptions)

    def inputPath(self):
        while True:
            path = input("Type your images' directory:\n")
            if os.path.exists(path):
                self.path = path
                break
            else:
                print("Invalid Path")

    def getSortedImagesInfo(self):
        FORMAT = ["JPEG", "PNG", "BMP", "WEBP"]
        allNames = [name for name in os.listdir(self.path)]
        imgs = []
        for i in allNames:
            try:
                im = Image.open(os.path.join(self.path, i))
                im_type = im.format
                if im_type in FORMAT:
                    imgs.append((i, im.size))
            except Exception as e:
                if e.__class__.__name__ == "UnidentifiedImageError":
                    print(e)
        if len(imgs) < 2:
            raise Exception("No Images or just one in this directory.")
        print(f"Find {len(imgs)} Images.")
        self.imgs = imgs

    def sortImages(self, sortBy="name", reverse=False):
        if sortBy == "name":
            self.imgs.sort(key=lambda s: s[0], reverse=reverse)
        elif sortBy == "width":
            self.imgs.sort(key=lambda s: (s[1][0], s[0]), reverse=reverse)
        elif sortBy == "height":
            self.imgs.sort(key=lambda s: (s[1][1], s[0]), reverse=reverse)
        elif sortBy.endswith("time"):
            # 'mtime' or 'ctime'
            ts = eval(f"os.path.get{sortBy}")
            self.imgs.sort(
                key=lambda s: ts(os.path.join(self.path, s[0])), reverse=reverse
            )
        print(f"Images has been sorted by {sortBy}.")

    def inputRowOrColumn(self):
        n = len(self.imgs)
        while True:
            rows = input(
                f"Input rows(Number 1 ~ {n}) you wanna stitch, or ENTER directly to set columns:"
            )
            try:
                if rows == "":
                    columns = input(f"Input columns(Number 1 ~ {n}) you wanna stitch:")
                    columns = int(columns)
                else:
                    rows = int(rows)
            except ValueError:
                if columns == "":
                    print("Nothing Input!")
                print("Please input numbers only!")
            else:
                if rows:
                    self.rows = rows
                    self.columns = math.ceil(n / rows)
                elif columns:
                    self.columns = columns
                    self.rows = math.ceil(n / columns)
                print("Set up.")
                break

    def setLayoutDetails(
        self, isZigzag=True, isVertical=False, isRightToLeft=False, oneline=True
    ):
        n = [self.columns, self.rows][isVertical]
        spilted = [self.imgs[i : i + n] for i in range(0, len(self.imgs), n)]

        cfn = rfn = max  # keep original size for each image
        ctemplate = rtemplate = 0
        if self.keep == "width":
            cfn = min  # keep same width in same column
            ctemplate = float("inf")
        elif self.keep == "height":
            rfn = min  # keep same height in same row
            rtemplate = float("inf")

        columnWidth = [ctemplate] * self.columns
        rowHeight = [rtemplate] * self.rows
        group = [[]] * len(spilted)

        for i, item in enumerate(spilted):
            group[i] = []  # TRAP: Python nested list https://segmentfault.com/a/1190000019450201
            for j, (name, size) in enumerate(item):
                if not isZigzag and i % 2:
                    j = len(spilted[0]) - j - 1
                if isVertical:
                    if isRightToLeft:
                        k = i
                        i = self.columns - i - 1
                        group[k].append((name, size, (i, j)))
                    else:
                        group[i].append((name, size, (i, j)))
                    columnWidth[i] = cfn(size[0], columnWidth[i])
                    rowHeight[j] = rfn(size[1], rowHeight[j])
                else:
                    columnWidth[j] = cfn(size[0], columnWidth[j])
                    rowHeight[i] = rfn(size[1], rowHeight[i])
                    group[i].append((name, size, (j, i)))

        # once again to fix global exrema value for dependent variables
        if self.keep == "width":
            if not oneline:
                columnWidth = [min(columnWidth)] * self.columns
            for sub in group:
                rowHeight[i] = max(
                    [h * columnWidth[x] / w for _, (w, h), (x, y) in sub]
                )
        elif self.keep == "height":
            if not oneline:
                rowHeight = [min(rowHeight)] * self.rows
            for sub in group:
                columnWidth[i] = max(
                    [w * rowHeight[y] / h for _, (w, h), (x, y) in sub]
                )

        print(columnWidth)
        print(rowHeight)
        self.columnWidth = columnWidth
        self.rowHeight = rowHeight
        self.group = group

    def drawOnCanvas(self, spacing, bgColor, verticalAlign, horizontalAlign):
        sW = self.columnWidth
        sH = self.rowHeight

        canvas = Image.new(
            "RGB",
            (
                (self.columns + 1) * spacing + round(sum(sW)),
                (self.rows + 1) * spacing + round(sum(sH)),
            ),
            bgColor,
        )

        for items in self.group:
            for name, (w, h), (x, y) in items:
                im = Image.open(os.path.join(self.path, name))
                if self.keep == "width" and sW[x] / w != 1:
                    w, h = sW[x], h * sW[x] / w
                    im = im.resize((round(w), round(h)), Image.ANTIALIAS)
                elif self.keep == "height" and sH[y] / h != 1:
                    w, h = w * sH[y] / h, sH[y]
                    im = im.resize((round(w), round(h)), Image.ANTIALIAS)

                if horizontalAlign == "left":
                    cX = spacing * (x + 1) + sum(sW[0:x])
                elif horizontalAlign == "right":
                    cX = spacing * (x + 1) + sum(sW[0 : x + 1]) - w
                else:
                    cX = spacing * (x + 1) + sum(sW[0:x]) + (sW[x] - w) / 2

                if verticalAlign == "top":
                    cY = spacing * (y + 1) + sum(sH[0:y])
                elif verticalAlign == "bottom":
                    cY = spacing * (y + 1) + sum(sH[0 : y + 1]) - h
                else:
                    cY = spacing * (y + 1) + sum(sH[0:y]) + (sH[y] - h) / 2

                print(name, (w, h), cX, cY)
                canvas.paste(im, (round(cX), round(cY)))
        self.collaged = canvas

    def save(
        self, saveFormat="JPEG", saveName="", saveDir="", **saveOptions,
    ):
        # https://pillow.readthedocs.io/en/5.1.x/reference/Image.html?highlight=save#PIL.Image.Image.save
        img = self.collaged
        ext = saveFormat
        if saveFormat.upper() in ["JPEG", "JPG"]:
            ext, saveFormat = "jpg", "JPEG"
        if not saveName:
            saveName = f"stitched_{int(time())}.{ext}"
        if not saveDir or not os.path.exists(saveDir):
            saveDir = ""
        fp = os.path.join(saveDir, saveName)
        img.save(fp, saveFormat, **saveOptions)
        img.show()


userDict = True
config = {
    "spacing": 20,
    "isVertical": True,
    "isRightToLeft": False,
    "isZigzag": False,
    "keep": "size",  # size, width, height
    "verticalAlign": "bottom",  # top, center, bottom
    "horizontalAlign": "right",  # left, center, right
    "oneline": True,  # determine wheather keep all lines but single line
    "sortBy": "name",  # width, height, ctime, mtime
    "sortAscending": True,
    "bgColor": "#EF5FA7",
    "saveName": "",
    "saveFormat": "JPEG",
    "saveDir": os.path.join(os.environ["USERPROFILE"], "Desktop"),
    "saveOptions": {
        "quality": 95,  # *FOR JPEG*: 1-95, 75 is default. Values above 95 should be avoided; 100 disables compression algorithm
        "optimize": False,  # If True, PNG compressing has no effect
        # "dpi": (x, y),
        # "compress_level": 6, # *FOR PNG*: 1(fastest)-9(best compression), 6 is default. 0 gives no compression.
    },
}

if __name__ == "__main__":
    if userDict:
        Stitcher(**config)
    else:
        Stitcher()
