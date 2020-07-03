# -*- coding: utf-8 -*-
# The third script I wrote in 2020-02-18

import os
import re


def func(path):
    path = path.replace('\\', '/').strip("'").strip('"').strip('/')
    names = os.listdir(path)
    asses = [x for x in names if x[-3:].lower() == 'ass']
    for ass in asses:
        assPath = f'{path}/{ass}'
        with open(assPath, encoding='utf-8') as f:
            data = f.read()
            part1, part2, part3 = re.split(
                r'(?<=styles\]\n|events\]\n)', data, 2, re.I)
            a, d = getPropertylist(part2, 'name', 'style')
            a = set(a)
            b = set(getPropertylist(part3, 'style', 'dialogue')[0])
            if '*default' in b:
                b.remove('*default'), b.add('default')
        c = '='*40
        print(f'{c}\nAS TO FILE "{ass}":')
        if a == b:
            print('Bingo! Exactly Similar!')
        else:
            e = a - b
            f = b - a 
            if e != set():
                def repl(obj):
                    if obj.group(1).strip(' ,\n').lower() in e:
                        return ''
                    else:
                        return obj.group(0)
                part2 = d.sub(repl, part2)
                with open(assPath, mode='w+', encoding='utf-8') as fp:
                    fp.write(f'{part1}{part2}{part3}')
                    print(', '.join(e), '----- removed because of redundancy.')
            if f != set():
                c = ', '.join(f)
                c = print(c, r'----- cannot find item(s) in [V4(+) Styles].')
    c = os.system('echo Press any key to continue... & pause > null')


def getPropertylist(string, str, prefix):
    formatLineList = re.split(
        r'\W+', re.match(r'Format:(.*?)\n', string, re.I).group(1).lower().strip(' '))
    r = formatLineList.index(str)
    if r + 1 != len(formatLineList):
        regex = re.compile(rf'{prefix}:(.*?,){{{r + 1}}}.*?\n', re.I)
    else:
        regex = re.compile(rf'{prefix}:(?:.*?,){{{r}}}(.*?\n)', re.I)
    return ([x.strip(' ,').lower() for x in regex.findall(string)], regex)


if __name__ == '__main__':
    path = input('Input dir you wanna batch process:')
    func(path)
