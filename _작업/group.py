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
    'rfp': {
        'label': '제안요청서 분석과 제안요약서',
        'sub': '제안요청서를 읽어 HTML 보고서를 만들고 그 내용으로 제안요약서를 만든 실행. '
               '만들기 전에 목차 열 장을 보여주고 승인을 받았다',
        'tabs': [
            ('rfp-deck', '자동'),
            ('rfp-sonnet', 'Sonnet 5'),
        ],
    },
    'close': {
        'label': '두 부서 마감 자료 대사',
        'sub': '같은 8월을 두고 반대 결론을 낸 자료 두 개를 주고 어디서 갈라지는지 '
               '찾게 한 실행. 같은 세 가지를 한 번에 시킨 쪽과 끊어서 시킨 쪽을 '
               '나란히 재 봤다',
        'tabs': [
            ('close-recon', '한 번에'),
            ('close-split', '끊어서'),
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
            with open(p, 'w', encoding='utf-8') as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1)
                fh.write('\n')  # 끝 줄바꿈이 없으면 돌릴 때마다 파일이 바뀐다
            n += 1
    print('회차 %d개를 묶음 %d개로 묶었습니다.' % (n, len(GROUPS)))


if __name__ == '__main__':
    main()
