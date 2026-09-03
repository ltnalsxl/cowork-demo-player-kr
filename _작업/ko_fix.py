# -*- coding: utf-8 -*-
"""한국어 하드룰 위반을 한 번에 걷어낸다.

connect  연결어미(-고/-며/-지만/-면서/-아서) 직후 쉼표 제거
         코드 블록과 표는 건드리지 않는다. 거기서는 쉼표가 값이다.
         "끝나서"처럼 어간과 어미가 붙어 표면형이 달라지는 경우까지 잡는다.

되돌리려면 README.orig.md가 있다.
"""
import io
import re
import sys

# -고/-며/-지만/-면서 계열은 형태가 고정이라 그대로 잡는다.
# -아서/-어서는 어간에 붙어 "끝나서·와서·해서"처럼 표면형이 바뀌므로 앞 음절까지 본다.
CONNECT = re.compile(
    r'((?:[가-힣]고|[가-힣]으며|[가-힣]며|[가-힣]지만|[가-힣]면서|[가-힣]서)),(?= )')

# 서술어가 아닌데 걸리는 말. "그리고," 같은 접속부사와 명사는 쉼표가 맞다.
KEEP = re.compile(r'(그리고|그러고|따라서|하지만|그래서|에서|보다|부터|까지|만큼|처럼|순서|절차|차례|"|」|\))$')


def strip_comma(path):
    lines = io.open(path, encoding='utf-8').read().split('\n')
    incode = False
    n = 0
    for i, l in enumerate(lines):
        if l.startswith('```'):
            incode = not incode
            continue
        if incode or l.lstrip().startswith('|'):
            continue

        def sub(m):
            if KEEP.search(m.group(1)):
                return m.group(0)
            return m.group(1)

        new, k = CONNECT.subn(sub, l)
        if new != l:
            lines[i] = new
            n += len(CONNECT.findall(l)) - len(CONNECT.findall(new))
    io.open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    return n


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('%-16s 연결어미 쉼표 %d곳 제거' % (p, strip_comma(p)))
