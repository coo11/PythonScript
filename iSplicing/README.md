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
    'is_vertical': True,
    'keep': 'height',  # `size` 保持每张图片大小不变, `height` 或 `width` 则保证按一行（列）中最小高（宽）度为基准缩放尺寸
    'sort_ascending': True, # 默认升序排列
    'sort_by': 0, # 图片拼接前可选按 `name - 0, width - 1, height - 2, ctime - 3, mtime - 4`排序，后两者指创建时间和修改时间
    'is_zigzag': False, # 是否按之字形排列图片；否则按一条龙排列
    'is_rtl': False, # 是否按照从左到右的顺序排列
    'inline': False,  # 确定是计算单行单列的最值，还是全部行列的最值
    'force_waterfall': False, # 是否强制瀑布流
    'vertical_align': 'top',  # 每张图片所在格的相对位置，可选 `top, center, bottom`
    'horizontal_align': 'left',  # 每张图片所在格的相对位置，可选 `top, center, bottom`
    'spacing': 10, # 每格图片间距
    'background_color': '#EF5FA7',  # 拼接画布的背景颜色
    }
```
