# -*- coding: utf-8 -*-
"""자동·보통으로 잰 회차를 한 줄에 세운 사다리.

모델과 노력을 고정하고 작업만 바꿔 돌린 값이라 서로 견줄 수 있다.
비교 대상이 뚜렷한 회차(모델 비교, 계정 비교)는 각자 표를 쓰고,
그 밖의 회차는 이 사다리를 쓴다.

값은 모두 실측이다. 여기 없는 조합은 만들지 않는다.
"""

# 크레딧 오름차순. 첫 항목이 "가장 적게 든" 기준이 된다.
LADDER = [
    {'name': '아침 브리핑', 'avg': 107,
     'meta': '읽고 Teams 메시지 하나 · 산출물 없음'},
    {'name': '주간보고 · 활동 없는 계정', 'avg': 219,
     'meta': '데이터 0건 · 지어내지 않고 멈춤'},
    {'name': '주간보고 · 사내 표준 서식', 'avg': 271,
     'meta': '서식 확인 + Word 1건 + Teams 요약'},
    {'name': '밀린 메일 정리', 'avg': 755,
     'meta': '400건 훑음 + Excel 1건 + 회신 초안 5건'},
    {'name': '출입기록 점검 · 스킬 만들기', 'avg': 789,
     'meta': '5턴 누적 · 메일 + 커스텀 스킬 + HTML 4개'},
    {'name': 'ISMS-P 심사 대응', 'avg': 1130,
     'meta': '문서 4종 · Word 편집 15회 거부'},
    {'name': '주간보고 · 활동 많은 계정', 'avg': 1178,
     'meta': '프로젝트 7건 · Word 1건 · 표 8개'},
]

HEAD = '자동·보통으로 잰 회차를 한 줄에 세우면'
LEAD = '모델과 노력을 고정하고 작업만 바꿔 돌린 실측값입니다.'
COND = ('모두 자동·보통입니다. 값을 가르는 것은 읽을 양 하나가 아니라 '
        '읽을 양과 만들 것이 함께 작용한 결과입니다. '
        '아침 브리핑은 읽고 메시지 하나를 보내고 끝나서 가장 적게 들었고, '
        '문서를 여러 개 만든 회차가 위로 갑니다.')


def bench(name, extra_cond=''):
    """사다리에서 name 행을 이 회차로 표시해 돌려준다."""
    rows = []
    found = False
    for m in LADDER:
        r = dict(m, n=1, effort='보통')
        if m['name'] == name:
            r['self'] = True
            found = True
        rows.append(r)
    if name and not found:
        raise ValueError('사다리에 없는 이름: %s' % name)
    return {
        'n': len(rows), 'people': 1,
        'min': min(m['avg'] for m in LADDER),
        'max': max(m['avg'] for m in LADDER),
        'head': HEAD, 'lead': LEAD,
        'condition': (COND + ' ' + extra_cond).strip(),
        'models': rows,
    }
