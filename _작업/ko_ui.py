# -*- coding: utf-8 -*-
"""화면에 나가는 문구를 다듬는다.

용어 통일  '노력' → '작업 수준'. 화면 선택기가 "작업 수준 보통"이라고 쓰는데
           설명문만 "노력"이면 같은 것을 두 이름으로 부르는 셈이다.
문장 다듬기 연결어미 뒤 쉼표, 호응이 어긋난 자리, 안 읽히는 표현.

빌드 스크립트를 고치므로 build_all.py를 다시 돌려야 반영된다.
"""
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 앞의 것부터 적용한다. 긴 문장을 먼저 두어 짧은 치환이 먼저 걸리지 않게 한다.
FIX = [
    # 용어 통일
    ('모델과 노력을 고정하고', '모델과 작업 수준을 고정하고'),
    ('모델과 노력을 고정하고 계정만 바꿨습니다.', '모델과 작업 수준을 고정하고 계정만 바꿨습니다.'),
    ('노력은 모델 기본값입니다.', '작업 수준은 모델 기본값을 그대로 뒀습니다.'),
    ('노력은 모델별 기본값을 그대로 뒀습니다.', '작업 수준은 모델마다 기본값을 그대로 뒀습니다.'),
    ('노력 기본값이 매우 높음이고, ', '작업 수준 기본값이 매우 높음이다. '),
    ('모델마다 기본 노력을 그대로 뒀다.', '모델마다 기본 작업 수준을 그대로 뒀다.'),
    ('모델과 노력 설정', '모델과 작업 수준 설정'),

    # 연결어미 뒤 쉼표
    ('집계해 메일로 보내고, 커스텀 스킬을', '집계해 메일로 보내고 커스텀 스킬을'),
    ('Word 편집이 15번 거부됐고, 주소록에', 'Word 편집이 15번 거부됐고 주소록에'),
    ('가장 적게 들었고, 문서를', '가장 적게 들었고 문서를'),
    ('"등록된 일정 없음"으로 적고 끝났고, 다른 쪽은',
     '"등록된 일정 없음"으로 적고 끝났습니다. 다른 쪽은'),
    ('답을 기다리는 건이 2건뿐이었고, 다른 쪽은',
     '답을 기다리는 건이 2건뿐이었습니다. 다른 쪽은'),

    # 호응이 어긋난 자리
    ('값을 가르는 것은 읽을 양 하나가 아니라 읽을 양과 만들 것이 함께 작용한 결과입니다.',
     '값은 읽을 양만으로 정해지지 않습니다. 읽을 양과 만들 것이 함께 작용합니다.'),

    # 안 읽히는 표현
    ('캘린더와 Teams가 비자 채우지 않고', '캘린더와 Teams에 아무것도 없자 채우지 않고'),
    ('회차마다 앞선 결과물을 정리해 서로 영향을 주지 않게 했습니다.',
     '회차마다 앞선 산출물을 지우고 돌려 서로 영향을 주지 않게 했습니다.'),
]

TARGETS = ['common.py', 'ladder.py', 'proofread_variants.py',
           'build_terra.py', 'build_sonnet.py', 'build_skill.py',
           'build_badge.py', 'build_isms.py', 'build_brief.py',
           'build_weekly.py', 'build_inbox.py']


def main():
    total = 0
    for name in TARGETS:
        p = os.path.join(BASE, name)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        before = s
        for a, b in FIX:
            s = s.replace(a, b)
        if s != before:
            io.open(p, 'w', encoding='utf-8').write(s)
            n = sum(before.count(a) for a, _ in FIX)
            total += n
            print('%-22s %d곳' % (name, n))
    print('모두 %d곳' % total)


if __name__ == '__main__':
    main()
