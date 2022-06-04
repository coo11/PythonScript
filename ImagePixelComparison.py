# https://stackoverflow.com/a/16721373/14168341
# Compare two images pixel by pixel
from PIL import Image, ImageChops
import os

point_table = ([0] + ([255] * 255))

def black_or_b(a, b):
    diff = ImageChops.difference(a, b) # https://stackoverflow.com/a/196882/14168341
    diff = diff.convert('L')
    diff = diff.point(point_table)
    new = diff.convert('RGB')
    new.paste(a, mask=diff)
    return diff

path_a = input("1st image path:\n")
a = Image.open(path_a)
path_b = input("2nd image path:\n")
b = Image.open(path_b)
c = black_or_b(a, b)
c.save(f'diff_{os.path.splitext(os.path.basename(path_a))[0]}.png')
d = black_or_b(b, a)
d.save(f'diff_{os.path.splitext(os.path.basename(path_b))[0]}.png')