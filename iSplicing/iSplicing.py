# -*- coding: utf-8 -*-
from pathlib import Path
from time import time
from PIL import Image


def ceil(n): return n.__ceil__()


class iSplicing:
    """A untility to splice irregular images"""

    SORT_BY_NAME = 0
    SORT_BY_WIDTH = 1
    SORT_BY_HEIGHT = 2
    SORT_BY_CREATE = 3
    SORT_BY_MODIFY = 4

    def __init__(
        self, *,
        sort_by=0,
        sort_ascending=True,
        rows=None,
        columns=None,
        is_vertical=False,
        keep="size",
        is_zigzag=False,
        is_rtl=False,
        inline=False,
        force_waterfall=False,
        vertical_align="top",
        horizontal_align="left",
        spacing=20,
        background_color='#333',
    ):
        self.is_vertical = is_vertical
        self.keep = keep
        self.input_working_path()
        self.filter_images()
        self.sort_images(sort_by, sort_ascending)
        self.ask_row_col(rows, columns)
        
        if force_waterfall:
            is_zigzag = False
        self.calc_layout(is_zigzag, is_rtl, inline)

        self.spacing = spacing
        self.background_color = background_color
        self.render(vertical_align, horizontal_align, force_waterfall)
        self.save()

    def input_working_path(self):
        while True:
            path_str = input("Type your images' directory:\n")
            path_str = path_str.strip("'").strip('"')
            working_path = Path(path_str)
            if working_path.exists() and working_path.is_dir():
                self.working_path = working_path
                break
            else:
                print("Invalid Path")

    def filter_images(self):
        FORMAT = ["JPEG", "PNG", "BMP", "WEBP", "GIF"]
        fps = [x for x in self.working_path.iterdir() if x.is_file()]
        imgs = []
        for fp in fps:
            try:
                with Image.open(fp) as im:
                    im = Image.open(fp)
                    im_type = im.format
                    if im_type in FORMAT:
                        imgs.append((fp, im.size))
            except Exception as e:
                if e.__class__.__name__ == "UnidentifiedImageError":
                    print(e)
        if len(imgs) < 2:
            raise Exception("No Images or just one in this directory.")
        print(f"Find {len(imgs)} Images.")
        self.imgs = imgs

    def sort_images(self, sort_by=0, sort_ascending=True):
        # fmt: off
        if sort_by == self.SORT_BY_NAME: key=lambda s: s[0]
        elif sort_by == self.SORT_BY_WIDTH: key=lambda s: (s[1][0], s[0])
        elif sort_by == self.SORT_BY_HEIGHT: key=lambda s: (s[1][1], s[0])
        elif sort_by == self.SORT_BY_CREATE: key=lambda s: s[0].stat().st_ctime
        elif sort_by == self.SORT_BY_MODIFY: key=lambda s: s[0].stat().st_mtime
        # fmt: on
        self.imgs.sort(key=key, reverse=not sort_ascending)

    def validate_row_col(self, rows=None, columns=None):
        n = len(self.imgs)
        try:
            rows = None if rows is None else int(rows)
            columns = None if columns is None else int(columns)
        except ValueError:
            print('ERROR: Invalid input.')
            return False
        if not rows and not columns:
            return False
        elif (rows and rows > n) or (columns and columns > n):
            print('ERROR: Input value out of range.')
            return False
        elif (rows and columns) and ceil(n/rows) != columns:
            print('ERROR: Input rows and columns are conflict.')
            return False
        else:
            _rows = columns and ceil(n / columns)
            _cols = rows and ceil(n / rows)
            if self.is_vertical and columns and ceil(n/_rows) != columns:
                print(
                    f'ERROR: Input columns "{columns}" is invalid if vertical aligned.')
                return False
            if not self.is_vertical and rows and ceil(n/_cols) != rows:
                print(
                    f'ERROR: Input rows "{rows}" is invalid if horizontal aligned.')
                return False
        self.rows = rows or ceil(n / columns)
        self.columns = columns or ceil(n / rows)
        print("Rows and columns are all valid.")
        return True

    def ask_row_col(self, rows=None, columns=None):
        if self.validate_row_col(rows, columns):
            pass
        else:
            n = len(self.imgs)
            while True:
                rows = input(
                    f"Input rows(Integer 1 ~ {n}) you wanna stitch, or ENTER directly to set columns:"
                )
                if not rows:
                    columns = input(
                        f"Input columns(Integer 1 ~ {n}) you wanna stitch:")
                if self.validate_row_col(rows, columns):
                    break

    def calc_layout(self, is_zigzag=False, is_rtl=False, inline=True):
        # Phase 1 对图片进行分组
        # 垂直（水平）排列图片，同列（行）归为一组，每组的步长为 step，以 step 为单位声明一个新的数组 matrix；
        step = self.rows if self.is_vertical else self.columns
        matrix = [self.imgs[i: i + step]
                  for i in range(0, len(self.imgs), step)]

        # Phase 2 确定需要锚定的边长，是保证范围内的图片列宽一致，还是行高一致？
        # （列和宽绑定，行和高绑定才是有意义的）
        cfn = rfn = max
        ctemplate = rtemplate = 0
        if self.keep == "width":
            cfn = min
            ctemplate = float("inf")
        elif self.keep == "height":
            rfn = min
            rtemplate = float("inf")
        else:
            pass

        # Phase 3 根据个性化参数，以图片所在的格子为参考系，重新排列图片的「坐标」
        column_width = [ctemplate] * self.columns
        row_height = [rtemplate] * self.rows
        # 不要使用 `[[]] * len(matrix)`：https://segmentfault.com/a/1190000019450201
        group = [[] for i in range(len(matrix))]

        # 遍历是为了求得重新排列的图片，所在行（列）高（列）的最值
        for i, imgs in enumerate(matrix):
            for j, (imgp, size) in enumerate(imgs):
                _i = i  # ???
                # 「垂直第 i 列」内的第 j 行或「水平第 i 行」内的第 j 列
                if is_zigzag and i % 2:  # 若使用之字形排列，在该偶数基准列内，逆序调整本列内图片的排布；
                    j = len(matrix[0]) - j - 1
                if self.is_vertical:  # 垂直排列，求出第 i 列本列图片的宽度最值，该列第 j 行图片的高度最值；
                    if is_rtl:
                        k = i
                        _i = self.columns - i - 1
                        group[k].append((imgp, size, (_i, j)))
                    else:
                        group[i].append((imgp, size, (_i, j)))
                    # 保证列宽一致，遍历后求得每列的最小值，则行高无意义
                    column_width[_i] = cfn(size[0], column_width[_i])
                    # 保证行高一致，遍历后求得每行的最小值，则列宽无意义
                    row_height[j] = rfn(size[1], row_height[j])
                else:
                    if is_rtl:
                        k = j
                        j = self.columns - j - 1
                        group[i].append((imgp, size, (j, i)))
                    else:
                        group[i].append((imgp, size, (j, i)))
                    column_width[j] = cfn(size[0], column_width[j])
                    row_height[i] = rfn(size[1], row_height[i])

        # 再次遍历各个位置的图片，以上方代码求得的高（宽）的最值，按比例缩放宽（高）度值
        if self.keep == "width":
            if not inline:  # 如果是所有图片的宽，则以最小的宽度值为基准
                column_width = [min(column_width)] * self.columns
            row_height = [0] * self.rows
            for i in group:
                for _, (w, h), (x, y) in i:
                    row_height[y] = max(
                        row_height[y], h * column_width[x] / w)
        elif self.keep == "height":
            if not inline:
                row_height = [min(row_height)] * self.rows
            column_width = [0] * self.columns
            for i in group:
                for _, (w, h), (x, y) in i:
                    column_width[x] = max(
                        column_width[x], w * row_height[y] / h)
        else:
            pass

        print(column_width)
        print(row_height)
        self.column_width = column_width
        self.row_height = row_height
        self.group = group

    def render(self, vertical_align, horizontal_align, force_waterfall):
        sW = self.column_width
        sH = self.row_height
        spacing = self.spacing

        cW = (self.columns - 1) * spacing + round(sum(sW))
        cH = (self.rows - 1) * spacing + round(sum(sH))
        canvas = Image.new("RGB", (cW, cH), self.background_color)

        equalSpacingForNonKeepWidth = force_waterfall and not self.is_vertical and self.keep != "width"
        equalSpacingForNonKeepHeight = force_waterfall and self.is_vertical and self.keep != "height"
        maxH = maxW = 0

        for imgs in self.group:
            cX = cY = 0  # Just for force waterfall
            for imgp, (w, h), (x, y) in imgs:
                with Image.open(imgp) as im:
                    if self.keep == "width" and sW[x] / w != 1:
                        w, h = sW[x], h * sW[x] / w
                        im = im.resize((round(w), round(h)), Image.Resampling.LANCZOS)
                    elif self.keep == "height" and sH[y] / h != 1:
                        w, h = w * sH[y] / h, sH[y]
                        im = im.resize((round(w), round(h)), Image.Resampling.LANCZOS)

                    if equalSpacingForNonKeepWidth:
                        pass
                    elif horizontal_align == "left":
                        cX = spacing * x + sum(sW[0:x])
                    elif horizontal_align == "right":
                        cX = spacing * x + sum(sW[0: x + 1]) - w
                    elif horizontal_align == "center":
                        cX = spacing * x + sum(sW[0:x]) + (sW[x] - w) / 2

                    if equalSpacingForNonKeepHeight:
                        pass
                    elif vertical_align == "top":
                        cY = spacing * y + sum(sH[0:y])
                    elif vertical_align == "bottom":
                        cY = spacing * y + sum(sH[0: y + 1]) - h
                    elif vertical_align == "center":
                        cY = spacing * y + sum(sH[0:y]) + (sH[y] - h) / 2

                    print(imgp.name, (w, h), cX, cY)
                    canvas.paste(im, (round(cX), round(cY)))
                    if equalSpacingForNonKeepWidth:
                        cX += spacing + w
                    elif equalSpacingForNonKeepHeight:
                        cY += spacing + h

        self.canvas = canvas
        return canvas

    def add_outer_border(self):
        old = self.canvas
        w, h = old.size
        sp = self.spacing
        canvas = Image.new("RGB", (w + sp * 2, h + sp * 2),
                           self.background_color)
        canvas.paste(old, (sp, sp))
        old.close()
        self.canvas = canvas
        return canvas

    def save(self, *,
             save_dir="",
             save_name=f"stitched_{int(time())}",
             save_format="JPEG",
             save_options={  # https://pillow.readthedocs.io/en/5.1.x/reference/Image.html?highlight=save#PIL.Image.Image.save
                 # *FOR JPEG*: 1-95, 75 is default. Values above 95 should be avoided; 100 disables compression algorithm
                 "quality": 95,
                 # If True, PNG compressing has no effect
                 "optimize": True,
                 # "dpi": (x, y),
                 # "compress_level": 6, # *FOR PNG*: 1(fastest)-9(best compression), 6 is default. 0 gives no compression.
             },):
        if not save_dir:
            save_dir = Path.home() / 'Desktop'
            if not save_dir.exists() or save_dir.is_file():
                save_dir = Path.home()
        else:
            save_dir = Path(save_dir)
            if not save_dir.exists():
                save_dir.mkdir(parents=True, exist_ok=True)

        self.add_outer_border()
        img = self.canvas
        ext = save_format
        if save_format.upper() in ["JPEG", "JPG"]:
            ext, save_format = "jpg", "JPEG"
        fp = save_dir / f'{save_name}.{ext}'
        img.save(fp, save_format, **save_options)
        img.show()
        img.close()


userDict = True
config = {
    'is_vertical': True,
    'keep': "height",  # size, width, height
    'is_zigzag': False,
    'is_rtl': False,
    "inline": False,  # 确定是计算单行单列的最值，还是全部行列的最值
    'force_waterfall': False,
    "vertical_align": "top",  # top, center, bottom
    "horizontal_align": "left",  # left, center, right
    "spacing": 10,
    "background_color": "#EF5FA7",  # "#C0C0C0",
}

if __name__ == "__main__":
    if userDict:
        iSplicing(**config)
    else:
        iSplicing()
