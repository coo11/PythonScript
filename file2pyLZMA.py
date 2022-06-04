# -*- coding: utf-8 -*-

import lzma
from base64 import b64encode
from io import BytesIO
from pathlib import Path

def main(path_str):
  path_str = path_str.strip("'").strip('"')
  p = Path(path_str)
  if p.exists() and not p.is_dir(): dash(p)
  else: print('Invalid file path.')
  main(input("File path:\n"))

def dash(p):
  with open(p, 'rb') as f:
    with open(str(p) + '.py', 'w', encoding = 'utf-8') as g:
      compressed_str = b64encode(lzma.compress(f.read())).decode('utf-8').replace('\n', '')
      g.write(f'''# -*- coding: utf-8 -*-

import lzma
from base64 import b64decode
from io import BytesIO

file_like_obj = BytesIO(lzma.decompress(b64decode('{compressed_str}')))''')
  print('Compressed.')

if __name__ == '__main__':
  main(input("File path:\n"))