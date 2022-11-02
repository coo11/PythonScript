# -*- coding: utf-8 -*-
import re
from pathlib import Path
from time import time

from PIL import Image


def ceil(n): return n.__ceil__()
def ceil_test(n, s): return ceil(n / ceil(n / s)) == s


class iJoiner:
    '''A untility for stitching canvases'''

    def __init__(self, *, spacing=0, background_color='#333'):
        self.spacing = spacing
        self.background_color = background_color

    def add_outer_border(self):
        old = self.canvas
        w, h = old.size
        sp = self.spacing
        if sp > 0:
            canvas = Image.new("RGB", (w + sp * 2, h + sp * 2),
                            self.background_color)
            canvas.paste(old, (sp, sp))
            old.close()
            self.canvas = canvas
        return self

    def render(self, canvas_arr, cmd_str):
        # canvas_arr = [c0,c1,c2,c3,....,cn-1,cn]
        # like ffmpeg -filter_complex: cmd_str = '[0][1]R[N1];[2][N1]B[N2];[4][5]B[N3];[N2][N3]R[OUTPUT]'
        mid_product = {}
        sp = self.spacing
        for sub_cmd in cmd_str.split(';'):
            sub_cmd = sub_cmd.strip()
            pre, loc, out = re.findall(
                r'^((?:\[\w+\]){2,})(L|R|T|B)\[(\w+)\]$', sub_cmd, re.I)[0]
            input_canvas = []
            for obj in re.finditer(r'\[(\w+)\]', pre):
                k = obj.group(1)
                if k in mid_product:
                    input_canvas.append(mid_product[k])
                else:
                    input_canvas.append(canvas_arr[int(k)])
            canvas_size = [c.size for c in input_canvas]
            is_horizontal = loc == 'L' or loc == 'R'
            ref = min(list(zip(*canvas_size))[is_horizontal])
            if is_horizontal:
                resized_size = [(round(w * ref / h), ref)
                                for (w, h) in canvas_size]
                new_side = list(zip(*resized_size))[0]
                new_size = (sum(new_side) + sp * (len(input_canvas) - 1), ref)
            else:
                resized_size = [(ref, round(h * ref / w))
                                for (w, h) in canvas_size]
                new_side = list(zip(*resized_size))[1]
                new_size = (ref, sum(new_side) + sp * (len(input_canvas) - 1))
            new_canvas = Image.new('RGB', new_size, self.background_color)
            cX = cY = 0
            for i, (w, h) in enumerate(resized_size):
                im = input_canvas[i].resize((w, h),
                                            Image.Resampling.LANCZOS)
                new_canvas.paste(im, (cX, cY))
                if is_horizontal:
                    cX += w + sp * (i + 1)
                else:
                    cY += h + sp * (i + 1)
            mid_product[out] = new_canvas

        self.canvas = mid_product['OUTPUT']
        del mid_product['OUTPUT']
        for i in mid_product:
            mid_product[i].close()
        for i in canvas_arr:
            i.close()
        return self

    def save(self, *,
             save_dir="", save_name=f"stitched_{int(time())}", save_format="JPEG",
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


class iSplicing(iJoiner):
    """A untility for splicing irregular images"""

    SORT_BY_NAME = 0
    SORT_BY_WIDTH = 1
    SORT_BY_HEIGHT = 2
    SORT_BY_CREATE = 3
    SORT_BY_MODIFY = 4

    def __init__(
        self, *,
        # Initialize input image(s)
        working_dir=None, sort_by=0, sort_ascending=True,
        # Parameters need validate
        is_vertical=False, rows=None, columns=None,
        # Calculating layout influenced by
        keep="size", is_zigzag=False, is_rtl=False, inline=False,
        # Rendering canvas influenced by
        force_waterfall=False, vertical_align="top", horizontal_align="left",
        spacing=20, background_color='#333'
    ):
        super(iSplicing, self).__init__(
            spacing=spacing, background_color=background_color)
        self.input_working_dir(working_dir)
        self.sort_by = sort_by
        self.sort_ascending = sort_ascending
        self.filter_images()
        # DO NOT CHANGE ASSIGNMENT ORDER
        self.is_vertical = is_vertical
        self.is_zigzag = False if force_waterfall else is_zigzag
        self.is_rtl = is_rtl
        self.inline = inline
        self.keep = keep

        if rows == columns == None:
            if is_vertical:
                self.columns = 1
            else:
                self.rows = 1
        elif not self.validate_row_col(rows=rows, columns=columns):
            self.ask_row_col()
        else:
            self.calc_layout()

        self.force_waterfall = force_waterfall
        self.vertical_align = vertical_align
        self.horizontal_align = horizontal_align

    @property
    def rows(self): return self._rows

    @rows.setter
    def rows(self, rows):
        if not hasattr(self, '_rows'):
            self._rows = None
        if self._rows == rows:
            pass
        if self.validate_row_col(rows=rows):
            self.calc_layout()
        else:
            self.ask_row_col()

    @property
    def columns(self): return self._columns

    @columns.setter
    def columns(self, columns):
        if not hasattr(self, '_colmuns'):
            self._columns = None
        if self._columns == columns:
            pass
        elif self.validate_row_col(columns=columns):
            self.calc_layout()
        else:
            self.ask_row_col()

    def input_working_dir(self, dir_str=None):
        if dir_str is None:
            pass
        elif not Path(dir_str).is_dir():
            print('Given path is not existed.')
        else:
            self.working_dir = Path(dir_str)
            return
        while True:
            dir_str = input("Type your images' directory:\n")
            dir_str = dir_str.strip("'").strip('"')
            working_dir = Path(dir_str)
            if working_dir.is_dir():
                self.working_dir = working_dir
                break
            else:
                print("Invalid Path.")

    def filter_images(self):
        FORMAT = ["JPEG", "PNG", "BMP", "WEBP", "GIF"]
        fps = [x for x in self.working_dir.iterdir() if x.is_file()]
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
        if len(imgs) < 1:
            raise Exception("No Images found in current directory.")
        else:
            self.imgs = imgs
            if len(imgs) == 1:
                self._rows = self._columns = 1
            else:
                self.sort_images()
                print(f"Find {len(imgs)} Images.")

    def sort_images(self):
        sb = self.sort_by
        # fmt: off
        if sb == self.SORT_BY_NAME: key=lambda s: s[0]
        elif sb == self.SORT_BY_WIDTH: key=lambda s: (s[1][0], s[0])
        elif sb == self.SORT_BY_HEIGHT: key=lambda s: (s[1][1], s[0])
        elif sb == self.SORT_BY_CREATE: key=lambda s: s[0].stat().st_ctime
        elif sb == self.SORT_BY_MODIFY: key=lambda s: s[0].stat().st_mtime
        # fmt: on
        self.imgs.sort(key=key, reverse=not self.sort_ascending)

    def validate_row_col(self, *, rows=None, columns=None):
        n = len(self.imgs)
        try:
            rows = None if not rows else int(rows)
            columns = None if not columns else int(columns)
        except ValueError:
            print('ERROR: Rows or columns value is not an integer.')
            return False
        if not rows and not columns:
            return False
        elif (rows and (rows > n or rows < 1)) or (columns and (columns > n or columns < 1)):
            print('ERROR: Rows or columns value is out of range.')
            return False
        elif (rows and columns) and ceil(n / rows) != columns:
            print('ERROR: Rows and columns are conflict.')
            return False
        else:
            if self.is_vertical and columns and not ceil_test(n, columns):
                print(
                    f'ERROR: Columns value "{columns}" is invalid if vertical aligned.')
                return False
            if not self.is_vertical and rows and not ceil_test(n, rows):
                print(
                    f'ERROR: Rows value "{rows}" is invalid if horizontal aligned.')
                return False
        self._rows = rows or ceil(n / columns)
        self._columns = columns or ceil(n / rows)
        print("Rows and columns value validation passed.")
        return True

    def ask_row_col(self):
        n = len(self.imgs)
        while True:
            rows = input(
                f"Input rows(Integer 1 ~ {n}) you wanna stitch, or ENTER directly to set columns:"
            )
            if not rows:
                columns = input(
                    f"Input columns(Integer 1 ~ {n}) you wanna stitch:")
            if self.validate_row_col(rows, columns):
                self.calc_layout()
                break

    def calc_layout(self):
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
                if self.is_zigzag and i % 2:  # 若使用之字形排列，在该偶数基准列内，逆序调整本列内图片的排布；
                    j = len(matrix[0]) - j - 1
                if self.is_vertical:  # 垂直排列，求出第 i 列本列图片的宽度最值，该列第 j 行图片的高度最值；
                    if self.is_rtl:
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
                    if self.is_rtl:
                        k = j
                        j = self.columns - j - 1
                        group[i].append((imgp, size, (j, i)))
                    else:
                        group[i].append((imgp, size, (j, i)))
                    column_width[j] = cfn(size[0], column_width[j])
                    row_height[i] = rfn(size[1], row_height[i])

        # 再次遍历各个位置的图片，以上方代码求得的高（宽）的最值，按比例缩放宽（高）度值
        if self.keep == "width":
            if not self.inline:  # 如果是所有图片的宽，则以最小的宽度值为基准
                column_width = [min(column_width)] * self.columns
            row_height = [0] * self.rows
            for i in group:
                for _, (w, h), (x, y) in i:
                    row_height[y] = max(
                        row_height[y], h * column_width[x] / w)
        elif self.keep == "height":
            if not self.inline:
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

    def render(self):
        sW = self.column_width
        sH = self.row_height
        sp = self.spacing

        cW = (self.columns - 1) * sp + round(sum(sW))
        cH = (self.rows - 1) * sp + round(sum(sH))
        canvas = Image.new("RGB", (cW, cH), self.background_color)

        equalSpacingForNonKeepWidth = self.force_waterfall and not self.is_vertical and self.keep != "width"
        equalSpacingForNonKeepHeight = self.force_waterfall and self.is_vertical and self.keep != "height"
        maxH = maxW = 0

        for imgs in self.group:
            cX = cY = 0  # Just for force waterfall
            for imgp, (w, h), (x, y) in imgs:
                with Image.open(imgp) as im:
                    if self.keep == "width" and sW[x] / w != 1:
                        w, h = sW[x], h * sW[x] / w
                        im = im.resize((round(w), round(h)),
                                       Image.Resampling.LANCZOS)
                    elif self.keep == "height" and sH[y] / h != 1:
                        w, h = w * sH[y] / h, sH[y]
                        im = im.resize((round(w), round(h)),
                                       Image.Resampling.LANCZOS)

                    if equalSpacingForNonKeepWidth:
                        pass
                    elif self.horizontal_align == "left":
                        cX = sp * x + sum(sW[0:x])
                    elif self.horizontal_align == "right":
                        cX = sp * x + sum(sW[0: x + 1]) - w
                    elif self.horizontal_align == "center":
                        cX = sp * x + sum(sW[0:x]) + (sW[x] - w) / 2

                    if equalSpacingForNonKeepHeight:
                        pass
                    elif self.vertical_align == "top":
                        cY = sp * y + sum(sH[0:y])
                    elif self.vertical_align == "bottom":
                        cY = sp * y + sum(sH[0: y + 1]) - h
                    elif self.vertical_align == "center":
                        cY = sp * y + sum(sH[0:y]) + (sH[y] - h) / 2

                    print(imgp.name, (w, h), cX, cY)
                    canvas.paste(im, (round(cX), round(cY)))
                    if equalSpacingForNonKeepWidth:
                        cX += sp + w
                    elif equalSpacingForNonKeepHeight:
                        cY += sp + h

        self.canvas = canvas
        return self


if __name__ == "__main__":
    if True:
        iSplicing(**{
            'is_vertical': False,
            'keep': "height",  # size, width, height
            'is_zigzag': False,
            'is_rtl': False,
            "inline": False,  # 确定是计算单行单列的最值，还是全部行列的最值
            'force_waterfall': False,
            "vertical_align": "top",  # top, center, bottom
            "horizontal_align": "left",  # left, center, right
            "spacing": 0,
            "background_color": "#EF5FA7",  # "#C0C0C0",
        }).render().save()
    else:
        # TODO
        pass
