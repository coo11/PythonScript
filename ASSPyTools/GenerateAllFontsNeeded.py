# -*- coding: utf-8 -*-
# The fourth script I wrote in 2020-02-18

import os
import re


def func(path):
    path = path.replace('\\', '/').strip("'").strip('"').strip('/')
    names = os.listdir(path)
    asses = [x for x in names if x[-3:].lower() == 'ass']
    details = ''
    fonts = set()
    for ass in asses:
        details += '='*40 + f'\n{ass}\n'
        assPath = f'{path}/{ass}'
        with open(assPath, encoding='utf-8') as f:
            data = f.read()
            part = re.split(r'(?<=styles\]\n|events\]\n)', data, 2, re.I)[1]
            formatLineList = re.split(
                r'\W+', re.match(r'Format:(.*?)\n', part, re.I).group(1).lower().strip(' '))
            r = formatLineList.index('fontname')
            if r + 1 != len(formatLineList):
                regex = re.compile(rf'style:(.*?,){{{r + 1}}}.*?\n', re.I)
            else:
                regex = re.compile(rf'style:(?:.*?,){{{r}}}(.*?\n)', re.I)
            a = set([x.strip(' ,').lower() for x in regex.findall(part)])
            details += '  |  '.join(a) + '\n'
            fonts = fonts | a
    summary = '+' * 40 + \
        '\nNeeded Font(s) Summary\n' + '  |  '.join(fonts) + '\n' + '+' * 40
    print(summary)
    details += summary
    b = input(
        'All fonts displayed. Do you want to get more details? [Enter] to save.')
    if b == '':
        import time
        name = f'FontsNeeded_{int(time.time())}.txt'
        path = f'{path}/{name}'
        with open(path, mode='w+') as f:
            f.write(details)
        os.startfile(path)


if __name__ == '__main__':
    path = input(
        'Input dir you wanna get info and details will be saved in it:')
    func(path)
