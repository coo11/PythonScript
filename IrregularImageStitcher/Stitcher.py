# -*- coding: utf-8 -*-
from PIL import Image, ImageOps
from time import time
import os
import math


class Stitcher:
    """A tool to stitch images in one"""

    def __init__(
        self,
        *,
        spacing=20,
        forceEqualSpacing=False,
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
        self.isVertical = isVertical
        if not isZigzag:
            forceEqualSpacing = False
        
        self.setLayoutDetails(isZigzag, isRightToLeft)
        self.drawOnCanvas(spacing, bgColor, verticalAlign,
                          horizontalAlign, forceEqualSpacing)
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
        FORMAT = ["JPEG", "PNG", "BMP", "WEBP", "GIF"]
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
                    columns = input(
                        f"Input columns(Number 1 ~ {n}) you wanna stitch:")
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
        self, isZigzag=True, isRightToLeft=False, oneline=True
    ):
        # 垂直（水平）排列图片，同列（行）归为一组，每组包含的图片数至多和行（列）数相等；
        n = [self.columns, self.rows][self.isVertical]
        spilted = [self.imgs[i: i + n] for i in range(0, len(self.imgs), n)]

        cfn = rfn = max
        ctemplate = rtemplate = 0
        # 让所有图片以最小宽（高）为基准：不需要考虑左右（上下）对齐；需要先求得每列（行）最小宽（高）度值
        if self.keep == "width":
            cfn = min
            ctemplate = float("inf")
        elif self.keep == "height":
            rfn = min
            rtemplate = float("inf")
        else:
            pass  # 不改变原尺寸

        columnWidth = [ctemplate] * self.columns
        rowHeight = [rtemplate] * self.rows
        group = [[]] * len(spilted)

        for i, item in enumerate(spilted):
            # TRAP: Python nested list https://segmentfault.com/a/1190000019450201
            group[i] = []
            for j, (name, size) in enumerate(item):
                if not isZigzag and i % 2:
                    j = len(spilted[0]) - j - 1
                if self.isVertical:  # 垂直排列，求出第 i 列本列图片的宽度最值，该列第 j 行图片的高度最值；
                    if isRightToLeft:  # 垂直排列时需考虑图片从左右哪一边开始
                        k = i
                        i = self.columns - i - 1
                        group[k].append((name, size, (i, j)))
                    else:
                        group[i].append((name, size, (i, j)))
                    columnWidth[i] = cfn(size[0], columnWidth[i])
                    rowHeight[j] = rfn(size[1], rowHeight[j])
                else:  # 水平排列，求出第 i 行本行图片的高度最值，该行第 j 列图片的宽度最值；
                    columnWidth[j] = cfn(size[0], columnWidth[j])
                    rowHeight[i] = rfn(size[1], rowHeight[i])
                    group[i].append((name, size, (j, i)))

        # 再次遍历各个位置的图片，以上方代码求得的高（宽）的最值，按比例缩放宽（高）度值，求得真实的宽（高）最值；
        if self.keep == "width":
            if not oneline:
                columnWidth = [min(columnWidth)] * self.columns
            _group = list(zip(*group)) if self.isVertical else group
            for i, sub in enumerate(group):
                rowHeight[i] = max(
                    [h * columnWidth[x] / w for _, (w, h), (x, y) in sub]
                )
        elif self.keep == "height":
            if not oneline:
                rowHeight = [min(rowHeight)] * self.rows
            print(group)
            _group = group if self.isVertical else list(zip(*group))
            for i, sub in enumerate(_group):
                columnWidth[i] = max(
                    [w * rowHeight[y] / h for _, (w, h), (x, y) in sub]
                )
        elif self.keep == "size":
            pass

        print(columnWidth)
        print(rowHeight)
        self.columnWidth = columnWidth
        self.rowHeight = rowHeight
        self.group = group

    def drawOnCanvas(self, spacing, bgColor, verticalAlign, horizontalAlign, forceEqualSpacing):
        sW = self.columnWidth
        sH = self.rowHeight

        cW = (self.columns + 1) * spacing + round(sum(sW))
        cH = (self.rows + 1) * spacing + round(sum(sH))
        canvas = Image.new("RGB", (cW, cH), bgColor)

        equalSpacingForNonKeepWidth = forceEqualSpacing and not self.isVertical and self.keep != "width"
        equalSpacingForNonKeepHeight = forceEqualSpacing and self.isVertical and self.keep != "height"
        fixedPaddingH = fixedPaddingW = 0
        maxH = maxW = 0

        for items in self.group:
            cX = cY = spacing  # Just for forceEqualSpacing
            for name, (w, h), (x, y) in items:
                im = Image.open(os.path.join(self.path, name))
                if self.keep == "width" and sW[x] / w != 1:
                    w, h = sW[x], h * sW[x] / w
                    im = im.resize((round(w), round(h)), Image.ANTIALIAS)
                elif self.keep == "height" and sH[y] / h != 1:
                    w, h = w * sH[y] / h, sH[y]
                    im = im.resize((round(w), round(h)), Image.ANTIALIAS)

                if equalSpacingForNonKeepWidth:
                    pass
                elif horizontalAlign == "left":
                    cX = spacing * (x + 1) + sum(sW[0:x])
                elif horizontalAlign == "right":
                    cX = spacing * (x + 1) + sum(sW[0: x + 1]) - w
                elif horizontalAlign == "center":
                    cX = spacing * (x + 1) + sum(sW[0:x]) + (sW[x] - w) / 2

                if equalSpacingForNonKeepHeight:
                    pass
                elif verticalAlign == "top":
                    cY = spacing * (y + 1) + sum(sH[0:y])
                elif verticalAlign == "bottom":
                    cY = spacing * (y + 1) + sum(sH[0: y + 1]) - h
                elif verticalAlign == "center":
                    cY = spacing * (y + 1) + sum(sH[0:y]) + (sH[y] - h) / 2

                print(name, (w, h), cX, cY)
                canvas.paste(im, (round(cX), round(cY)))
                if equalSpacingForNonKeepHeight:
                    cY += spacing + h
                elif equalSpacingForNonKeepWidth:
                    cX += spacing + w
            if equalSpacingForNonKeepHeight:
                maxH = max(cY, maxH)
                fixedPaddingH = maxH - cH
            elif equalSpacingForNonKeepWidth:
                maxW = max(cX, maxW)
                fixedPaddingW = maxW - cW

        if fixedPaddingH or fixedPaddingW:
            canvas = ImageOps.expand(
                canvas, (0, 0, round(fixedPaddingW), round(fixedPaddingH)))
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
    "forceEqualSpacing": True, # Similar with waterfall
    "isVertical": False,
    "isRightToLeft": False,
    "isZigzag": True,  # Conflict with forceEqualSpacing enabled if false!!!
    "keep": "height",  # size, width, height
    "verticalAlign": "top",  # top, center, bottom
    "horizontalAlign": "left",  # left, center, right
    "oneline": False,  # 确定是计算单行单列的最值，还是全部行列的最值
    "sortBy": "name",  # width, height, ctime, mtime
    "sortAscending": True,
    "bgColor": "#C0C0C0",  # "#C0C0C0",
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
