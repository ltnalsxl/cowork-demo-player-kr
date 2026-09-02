# -*- coding: utf-8 -*-
"""자동·보통 회차는 로그를 JSON에 직접 들고 있다.

로그는 그대로 두고 공유 값(벤치마크, 산출물)만 common.py에서 다시 받아 온다.
여러 번 돌려도 결과가 같다.
"""
import json
import os

import common as C

BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, 'runs', 'tc04-auto.json')

d = json.load(open(P, encoding='utf-8'))
d['bench'] = C.TC04_BENCH
d['artifacts'] = C.ART_AUTO
d['prompt'] = C.TC04_PROMPT
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('tc04-auto.json  공유 값 갱신  로그 %d단계' % len(d['log']))
