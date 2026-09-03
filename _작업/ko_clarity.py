# -*- coding: utf-8 -*-
"""korean-clarity 3단계 진단. 읽고 바로 이해되는지만 본다.

문법도 맞고 AI 티도 없는데 읽으면 "무슨 말이지?" 싶은 자리를 찾는다.
코드 블록과 표는 건드리지 않는다.
"""
import io
import re
import sys

PATTERNS = [
    ('추상 명사화', r'[가-힣]{2,}성을 (?:가진|지닌)|[가-힣]{2,}화의 [가-힣]{2,}화'),
    ('정의문 도치', r'것은 [^.]{2,24}(?:이다|입니다)'),
    ('막연한 대명사', r'(?:^|[ .])이는 [가-힣]'),
    ('실무 밖 한자어', r'금번|당해|소기의|익일|명기|제고|기 제출'),
    ('주어 슬쩍 바뀜', r'습니다\. 이는 '),
    ('혼자 못 서는 제목', r'^#{2,4} [가-힣A-Za-z]{1,4}$'),
    ('이중 부정', r'없지 않|않지 않|아니지 않'),
    ('긴 관형절', r'(?:[가-힣]+(?:하는|되는|있는|없는) ){3,}[가-힣]'),
]


def scan(path):
    lines = io.open(path, encoding='utf-8').read().split('\n')
    incode = False
    hits = []
    for i, l in enumerate(lines, 1):
        if l.startswith('```'):
            incode = not incode
            continue
        if incode or l.lstrip().startswith('|'):
            continue
        for name, pat in PATTERNS:
            m = re.search(pat, l)
            if m:
                hits.append((name, i, l.strip()[:90]))
    return hits


if __name__ == '__main__':
    for p in sys.argv[1:]:
        h = scan(p)
        print('%s  %d건' % (p, len(h)))
        for name, i, txt in h:
            print('  %-14s %4d| %s' % (name, i, txt))
