# -*- coding: utf-8 -*-
"""비교 블록에 축 표시를 넣는다.

크레딧 비교는 세 축으로 갈린다. 무엇을 고정하고 무엇만 바꿨는지가
축이다. 축을 데이터에 적어 두면 모아보기가 이 값으로 묶는다.

  모델  같은 일을 모델만 바꿔 돌린 회차
  계정  같은 일을 계정만 바꿔 돌린 회차
  작업  모델과 작업 수준을 고정하고 작업만 바꾼 회차

작업 축 표는 세 실행이 똑같은 것을 나눠 갖고 있다. 그쪽에는 shared를
달아 실행 안에서는 짧게만 보여 주고 전체 표는 모아보기로 넘긴다.

사용법: python mark_bench_axis.py
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BASE, 'runs')

AXIS = {
    'tc04-sonnet': '모델',
    'tc04-terra': '모델',
    'skill-proofread': '모델',
    'rfp-deck': '모델',
    'rfp-sonnet': '모델',
    'daily-brief': '계정',
    'inbox-triage': '계정',
    'weekly-team': '작업',
    'badge-check': '작업',
    'isms-audit': '작업',
}

# 세 실행이 같은 표를 나눠 갖는다. 실행 안에서는 접어 두고 모아보기로 넘긴다.
SHARED = ('weekly-team', 'badge-check', 'isms-audit')

# 모아보기는 머리글로 표를 묶는다. 비어 있으면 실행 제목으로 떨어져 결이 어긋난다.
HEADS = {
    'tc04-sonnet': ('같은 딥리서치를 모델만 바꿔 돌리면',
                    '같은 프롬프트로 조사와 문서 작성까지 시킨 실측값입니다.'),
    'tc04-terra': ('같은 딥리서치를 모델만 바꿔 돌리면',
                   '같은 프롬프트로 조사와 문서 작성까지 시킨 실측값입니다.'),
}

# 공유 표의 측정 조건은 실행마다 꼬리가 다르다. 모아보기에서는 공통분만 쓴다.
SHARED_COND = (
    '모두 자동·보통입니다. 값은 읽을 양만으로 정해지지 않습니다. 읽을 양과 만들 것이 '
    '함께 작용합니다. 아침 브리핑은 읽고 메시지 하나를 보내고 끝나서 가장 적게 들었고 '
    '문서를 여러 개 만든 회차가 위로 갑니다.'
)


def main():
    for name, axis in AXIS.items():
        p = os.path.join(RUNS, name + '.json')
        with open(p, encoding='utf-8') as f:
            r = json.load(f)
        b = r.get('bench')
        if not b:
            print('건너뜀 %s (bench 없음)' % name)
            continue
        b['axis'] = axis
        if name in HEADS:
            b.setdefault('head', HEADS[name][0])
            b.setdefault('lead', HEADS[name][1])
        if name in SHARED:
            b['shared'] = True
            b['sharedCondition'] = SHARED_COND
        else:
            b.pop('shared', None)
            b.pop('sharedCondition', None)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('%-16s %s축%s' % (name, axis, ' · 공유' if name in SHARED else ''))

    subprocess.check_call([sys.executable, os.path.join(BASE, 'build.py')])


if __name__ == '__main__':
    main()
