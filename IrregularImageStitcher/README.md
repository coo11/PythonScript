# 不规则多宫格图片拼接

一个可以自定义众多参数的不规则图片拼接脚本。

## 使用

安装 `Pillow` 模块:

```
pip install Pillow
```

可修改脚本末尾的字典配置各项参数：

```Python
config = {
    "spacing": 20,  # 每格图片间距
    "isVertical": True, # 是否垂直排列图片
    "isRightToLeft": False,  # 垂直排列时有效，决定是否从右到左排列图片
    "isZigzag": False,  # 是否按之字形排列图片；否则按一条龙排列
    "keep": "size",  # `size` 保持每张图片大小不变, `height` 或 `width` 则保证按一行（列）中最小高（宽）度为基准缩放尺寸
    "oneline": True,  # 仅当 `keep` 参数为 `size` 时有效，是否仅仅以当前行（列）为基准缩放；否则所有图片按所有图片中最小的边长缩放。
    "verticalAlign": "bottom",  # 每张图片所在宫格的相对位置，可选 `top, center, bottom`
    "horizontalAlign": "right",  # 同上，可选 `left, center, right`
    "sortBy": "name",  # 图片拼接前可选按 `name, width, height, ctime, mtime`排序，后两者指创建时间和修改时间
    "sortAscending": True, # 默认升序排列；否则降序
    "bgColor": "#EF5FA7", # 拼接画布的背景颜色
    "saveName": "",
    "saveFormat": "JPEG",
    "saveDir": os.path.join(os.environ["USERPROFILE"], "Desktop"),
    "saveOptions": {
        "quality": 95,  # *FOR JPEG*: 1-95, 75 is default. Values above 95 should be avoided; 100 disables compression algorithm
        "optimize": False,  # If True, PNG compressing has no effect
        # "dpi": (x, y),
        # "compress_level": 6, # *FOR PNG*: 1(fastest)-9(best compression), 6 is default. 0 gives no compression.
    }
```