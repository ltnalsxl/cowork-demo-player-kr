# -*- coding: utf-8 -*-
"""같은 프롬프트를 조건만 바꿔 돌린 회차를 하나로 묶는다.

계정이나 모델을 바꾸면 로그 전체가 달라져서 답변만 갈아 끼울 수 없다.
그래서 회차는 그대로 두고, 홈에는 대표 하나만 세운 뒤 안에서 탭으로 오간다.

group      같은 묶음이면 같은 문자열
groupLabel 홈과 사이드바에 보일 이름
groupSub   홈 타일 설명. 없으면 대표 회차의 subtitle을 쓴다
tab        탭에 보일 짧은 이름
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BASE, 'runs')

GROUPS = {
    'tc04': {
        'label': '국내 피지컬AI 시장 동향 딥리서치',
        'sub': '같은 프롬프트를 모델만 바꿔 돌린 실행. '
               '비싼 쪽이 더 두꺼운 문서를 내지 않았다',
        'tabs': [
            ('tc04-sonnet', 'Sonnet 5'),
            ('tc04-terra', 'GPT 5.6 Terra'),
        ],
    },
    'tc01': {
        'label': '주간 업무보고 자동 작성',
        'sub': '같은 프롬프트를 활동이 많은 계정과 없는 계정에서 돌린 실행. '
               '읽을 것이 없자 지어내지 않고 멈췄다',
        'tabs': [
            ('tc01-demo', '활동 적은 계정'),
            ('tc01-real', '활동 많은 계정'),
        ],
    },
}


def main():
    n = 0
    for g, cfg in GROUPS.items():
        for i, (rid, tab) in enumerate(cfg['tabs']):
            p = os.path.join(RUNS, rid + '.json')
            d = json.load(open(p, encoding='utf-8'))
            d['group'] = g
            d['tab'] = tab
            # 대표(첫 항목)만 홈에 세울 이름과 설명을 든다.
            if i == 0:
                d['groupLabel'] = cfg['label']
                d['groupSub'] = cfg['sub']
            else:
                d.pop('groupLabel', None)
                d.pop('groupSub', None)
            json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            n += 1
    print('회차 %d개를 묶음 %d개로 묶었습니다.' % (n, len(GROUPS)))


if __name__ == '__main__':
    main()
