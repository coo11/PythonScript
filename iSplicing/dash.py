from iSplicing import iJoiner, iSplicing

a = iSplicing(**{
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
}).render().canvas

b = iSplicing(**{
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
}).render().canvas

g = iJoiner(spacing=0, background_color='#EF5FA7'
            ).render([a, b],
                     '[0][1]B[OUTPUT]'
                     ).save()
