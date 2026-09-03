# -*- coding: utf-8 -*-
"""실습-04 평일 아침 브리핑 자동화.

앞의 회차들과 다른 점은 한 번 시키고 끝나지 않는다는 것이다. Cowork가 짧은 요청을
상세 작업 설명으로 늘려 되풀이 작업으로 만들고, 승인하면 그 자리에서 한 번 돌린다.

같은 프롬프트를 계정 두 곳에서 돌렸다. 화면에 싣는 것은 일정이 많은 쪽이고,
일정이 0건인 계정에서 잰 95는 크레딧 표에만 남긴다. 그쪽은 캘린더가 비자
채우지 않고 "등록된 일정 없음"으로 적고 끝냈다.

이름, 조직, 부서명은 예시 값으로 바꿨고, 하는 일은 사내 교육팀으로 옮겨 각색했다.
바꾸지 않은 것: 도구 호출 순서와 횟수, 시각, 단계 구성, 모델과 노력 설정, 크레딧.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BASE, 'runs')

PROMPT = """평일 아침 7시 30분에 오늘의 브리핑을 나에게 Teams 메시지로 보내 줘.

담을 내용

하나. 오늘 회의 목록과 회의마다 준비할 것

둘. 답을 기다리는 메일 중 급한 것

셋. 이번 주에 기한이 있는 일

분량: 출근길에 한 번에 읽히게, 화면 한 번 분량

제약: 확인되지 않은 것은 지어내지 말고 표시해 줘."""

# Cowork가 짧은 요청을 늘려 되풀이 작업의 설명으로 삼는다.
# 승인하면 이 설명이 그대로 두 번째 프롬프트가 되어 즉시 한 번 돈다.
DESC_REAL = ('Copilot User의 오늘 하루 브리핑을 정리해서 Copilot User 본인에게 Teams 채팅 '
             '메시지로 보낸다. 내용은 세 부분: (1) 오늘 일정의 회의 목록 — 각 회의마다 시간, '
             '제목, 주요 참석자와 그 회의를 위해 미리 준비할 것(관련 메일/파일/이전 회의 '
             '내용에서 확인된 것만); 비공개·개인 일정은 제목 대신 \'개인 일정\'으로만 표시. '
             '(2) 회신을 기다리고 있는 메일 중 급한 것 — 보낸 사람, 요청 내용, 대기 기간. '
             '(3) 이번 주 안에 기한이 있는 일 — 메일·회의·메시지에서 확인된 마감이나 약속. '
             '분량은 휴대폰 화면 한 번에 읽히는 정도로 짧게, 불릿 위주로 한국어로 작성한다. '
             '확인되지 않았거나 자료에서 찾지 못한 내용은 절대 추측해서 채우지 말고 '
             '\'확인 필요\'로 표시한다. 해당 항목이 없으면 \'해당 없음\'이라고 적는다.')

DESC_DEMO = ('오늘의 브리핑을 작성해 사용자 본인에게 Teams 메시지(자기 자신과의 채팅)로 '
             '보낸다. 한국어로 작성하며, 출근길에 스마트폰 화면 한 번 분량으로 한 번에 '
             '읽히도록 짧고 간결하게 정리한다. 포함할 세 가지 항목: (1) 오늘 일정의 회의 '
             '목록 — 시간, 제목, 주요 참석자와 회의별로 미리 준비하거나 확인해야 할 것(관련 '
             '메일, 이전 회의 후속 조치, 안건 등 실제 확인된 내용 기준). 비공개(private)로 '
             '표시된 일정은 제목 대신 \'비공개 일정\'으로만 표기한다. (2) 사용자의 답장을 '
             '기다리고 있는 메일 중 급한 것 — 보낸 사람, 요지, 왜 급한지. (3) 이번 주 안에 '
             '기한이 있는 일 — 메일, 회의, 채팅에서 확인된 마감이나 약속. 근거는 실제로 '
             '조회한 일정, 메일, Teams 메시지에서만 가져오고, 확인되지 않았거나 추측이 필요한 '
             '부분은 지어내지 말고 \'확인 필요\' 또는 \'근거 없음\'으로 명확히 표시한다. '
             '해당 항목에 내용이 없으면 \'없음\'이라고 적는다.')

T_SCHED = ('This is a recurring request, not a one-off. Weekday mornings at 7:30 means a '
           'scheduled task rather than something I run once now. Let me turn the short brief '
           'into a full task description so the same rules apply every morning, then schedule it.')
T_RULE = ('The user said not to invent anything that is not confirmed. That has to be written '
          'into the task description itself, otherwise a future run with sparse data will pad '
          'the briefing. I will spell out 확인 필요 and 없음 as required outputs.')

BENCH = {
    'n': 2, 'people': 1, 'min': 95, 'max': 107,
    'head': '같은 브리핑을 일정이 다른 계정에서 시키면',
    'lead': '모델과 노력을 고정하고 계정만 바꿔 돌린 실측값입니다.',
    'condition': '한쪽은 오늘 일정이 0건이라 "등록된 일정 없음"으로 적고 끝났고, '
                 '다른 쪽은 회의 4건에 회신 대기 3건을 찾았습니다. '
                 '둘 다 읽기만 하고 문서는 만들지 않습니다.',
    'models': [
        {'name': '일정이 적은 계정', 'avg': 95, 'n': 1, 'effort': '보통',
         'meta': '일정 0건 · 메일 2건 · 산출물 없음'},
        {'name': '일정이 많은 계정', 'avg': 107, 'n': 1, 'effort': '보통',
         'meta': '회의 4건 · 회신 대기 3건 · 산출물 없음'},
    ],
}


# ── 실계정 회차 ────────────────────────────────────────────
T_REAL_1 = ('Calendar has four events today and two of them overlap between 10:00 and 11:00. '
            'That overlap is worth surfacing on its own — the user has to pick one on the way '
            'in. For prep notes I only have what the invitations and related mail actually say.')
T_REAL_2 = ('The mail pile is large, so I need to separate what is genuinely waiting on a reply '
            'from what is a notification. Three threads have an open question addressed to the '
            'user. One of them asks to choose between two dates, which is the most urgent.')
T_REAL_3 = ('For the prep line under each meeting I will write only what a mail or an invitation '
            'states. Where nothing states it, 확인 필요 is the honest answer and it keeps the '
            'briefing short. Padding it with plausible prep items would defeat the constraint.')

BRIEF_REAL = """☀️ **오늘의 브리핑 — 9월 3일(목)**

**오늘 회의**

- **08:00–11:00** 하반기 교육과정 설계 워크숍 (2안)
  준비: 확인 필요 — 사전 자료 안내 메일 없음
- **10:00–11:00** 신임 팀장 과정 리허설 ← 앞 회의와 겹침
  준비: 실습 계정 사전 등록 (등록 안내 메일 기준)
- **12:30–13:30** 교육 담당자 정례
  준비: 해당 없음
- **17:30–18:00** 사업장 교육 준비 (동료 A)
  준비: 지방 사업장 교육 자료 초안 — 9/8 확정 기한

**회신 대기**

- **동료 B**(영업본부) — 교육 일정 택일 요청(9/8 또는 9/9), 이틀째 대기
- **학습관리시스템** 추가 확인 사항 — 요청 내용 확인 필요
- **생산본부** 교육 자료 공유 링크 회신 대기

**이번 주 기한**

- 워크숍 주차 사전 등록
- 하반기 교육 예산 확정
- 9/8 지방 사업장 교육 자료 확정

근거: 오늘 캘린더, 최근 메일. 확인되지 않은 항목은 '확인 필요'로 적었습니다."""

FINAL_REAL = """오늘 아침 브리핑을 본인 Teams 채팅으로 보냈습니다.

요약하면:

- **회의 4건** — 08:00 하반기 교육과정 설계 워크숍(2안), 10:00 신임 팀장 과정 리허설(두 건 시간 겹침), 12:30 교육 담당자 정례, 17:30 사업장 교육 준비(동료 A)
- **회신 대기** — 동료 B(영업본부)의 교육 일정 택일 요청(9/8 또는 9/9)이 가장 급하고, 학습관리시스템 추가 확인 사항, 생산본부 교육 자료 공유 링크 회신 대기
- **이번 주 기한** — 워크숍 주차 사전 등록, 하반기 교육 예산 확정, 9/8 지방 사업장 교육 자료 확정

각 회의의 준비물은 메일에서 근거가 확인된 것만 적고, 나머지는 '확인 필요'로 표시했습니다."""

LOG_REAL = [
    {'t': 'think', 'label': '사고 과정', 'time': '오후 12:31', 'body': T_SCHED,
     'status': '되풀이 작업으로 만드는 중'},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 12:31', 'body': T_RULE,
     'status': '규칙을 문장으로 옮기는 중'},

    {'t': 'tool', 'icon': 'clock', 'label': '되풀이 작업 만들기', 'time': '오후 12:31',
     'status': '예약을 준비하는 중', 'act': '되풀이 작업을 만드는 중'},

    {'t': 'schedule', 'time': '오후 12:31',
     'name': '평일 아침 브리핑 (Teams)', 'every': '평일', 'at': '오전 7:30', 'where': '새 대화',
     'desc': DESC_REAL,
     'status': '예약 승인을 기다리는 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'approved', 'time': '오후 12:33', 'label': '1개 작업 승인됨',
     'status': '예약을 등록하는 중'},

    {'t': 'prompt', 'time': '오후 12:34', 'sep': '지금 한 번 실행', 'body': DESC_REAL},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 12:34',
     'status': '단계를 추적하는 중', 'act': '일정과 메일을 조회하는 중',
     'items': [
         {'think': True, 'body': T_REAL_1},
         {'icon': 'cal', 'tag': 'Outlook', 'label': '일정 보기', 'target': '오늘'},
         {'icon': 'mail', 'tag': 'Outlook', 'label': '메시지 나열', 'target': '최근 메일'},
         {'think': True, 'body': T_REAL_2},
         {'icon': 'struct', 'label': '이메일 목록 정리'},
         {'icon': 'file', 'label': '이메일 내용 확인'},
         {'icon': 'check', 'label': '이메일 제목 목록'},
     ]},

    {'t': 'tool', 'icon': 'search', 'label': '주요 메일 내용 확인', 'time': '오후 12:35',
     'status': '회신 대기 메일을 가리는 중', 'act': '메일 본문을 읽는 중'},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 12:35', 'body': T_REAL_3,
     'status': '근거 있는 것만 남기는 중'},

    {'t': 'tool', 'icon': 'teams', 'tag': 'Teams', 'time': '오후 12:36',
     'label': 'Teams 메시지 보내는 중:',
     'target': '☀️ 오늘의 브리핑 — 9월 3일(목) 오늘 회의 • 08:00–11:00 하반기 교육과정…',
     'status': '메시지를 만드는 중', 'act': 'Teams 메시지를 준비하는 중'},

    {'t': 'mail', 'chat': True, 'time': '오후 12:36',
     'to': 'me', 'body': BRIEF_REAL,
     'status': '요청 작업 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'approved', 'time': '오후 12:36', 'label': '1개 작업 승인됨',
     'status': '메시지를 보내는 중'},

    {'t': 'final', 'time': '오후 12:36', 'body': FINAL_REAL,
     'status': '완료', 'act': '작업 완료'},
]


data = {
    'id': 'daily-brief',
    'tc': '실습-04',
    'folder': '실습',
    'title': '평일 아침 브리핑 자동화',
    'chatTitle': '평일 아침 브리핑 · 되풀이 예약',
    'subtitle': '짧은 요청을 상세 작업 설명으로 늘려 평일 오전 7시 30분 되풀이 작업으로 남긴 실행. '
                '회의 4건과 회신 대기 3건을 찾아 한 화면에 담았다',
    'model': '자동',
    'effort': '보통',
    'date': '2026년 9월 3일 목요일',
    'credit': 107,
    'note': '근거가 없는 준비물은 채우지 않고 확인 필요로 남깁니다.',
    'scheduled': {
        'name': '평일 아침 브리핑 (Teams)',
        'when': 'Every week on Monday, Tuesday, Wednesday, Thursday, Friday at 07:30',
    },
    'allowed': ['메시지 보내기'],
    'bench': BENCH,
    'steps': [],
    'skills': [],
    'tools': ['일정', 'Outlook', 'Teams'],
    'prompt': PROMPT,
    'promptTime': '오후 12:31',
    'log': LOG_REAL,
    'artifacts': [],
}

json.dump(data, open(os.path.join(RUNS, 'daily-brief.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for old in ('brief-real.json', 'brief-demo.json'):
    p = os.path.join(RUNS, old)
    if os.path.exists(p):
        os.remove(p)
print('daily-brief.json  로그 %d단계' % len(LOG_REAL))
