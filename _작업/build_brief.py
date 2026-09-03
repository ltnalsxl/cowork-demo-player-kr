# -*- coding: utf-8 -*-
"""실습-04 평일 아침 브리핑 자동화. 같은 프롬프트를 계정 두 곳에서 돌린 회차 쌍.

앞의 회차들과 다른 점은 한 번 시키고 끝나지 않는다는 것이다. Cowork가 짧은 요청을
상세 작업 설명으로 늘려 되풀이 작업으로 만들고, 승인하면 그 자리에서 한 번 돌린다.

brief-real  일정과 메일이 있는 계정. 회의 4건, 회신 대기 3건을 실제로 찾아냈다.
brief-demo  데모 테넌트. 캘린더가 비어 있자 채우지 않고 없다고 적었다.

실계정 회차의 이름, 조직, 고객사, 사내 프로그램명은 예시 값으로 바꿨다.
바꾸지 않은 것: 도구 호출 순서와 횟수, 시각, 단계 구성, 모델과 노력 설정.
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
    'n': 2, 'people': 1, 'min': 219, 'max': 1178,
    'head': '참고 · 같은 자동·보통 설정으로 측정한 회차',
    'lead': '이 회차는 크레딧을 재지 않았습니다. 아래는 모델과 노력을 같게 두고 '
            '계정만 바꿔 돌린 다른 작업의 실측값입니다.',
    'condition': '작업 종류가 달라 이 회차의 값으로 읽지 마십시오. '
                 '데이터 양이 크레딧을 얼마나 움직이는지만 보십시오.',
    'models': [
        {'name': '주간보고 · 활동 없는 계정', 'avg': 219, 'n': 1, 'effort': '보통',
         'meta': '자동·보통 · 데이터 0건'},
        {'name': '주간보고 · 활동 많은 계정', 'avg': 1178, 'n': 1, 'effort': '보통',
         'meta': '자동·보통 · 프로젝트 7건'},
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

- **08:00–11:00** 사내 기술 세션 시리즈 (Option 2)
  준비: 확인 필요 — 사전 자료 안내 메일 없음
- **10:00–11:00** 도입 프로그램 리프레셔 L300 ← 앞 회의와 겹침
  준비: 실습 계정 사전 등록 (등록 안내 메일 기준)
- **12:30–13:30** 지역 커뮤니티 콜
  준비: 해당 없음
- **17:30–18:00** 워크숍 준비 (동료 A)
  준비: 지방 사업장 교육 자료 초안 — 9/8 확정 기한

**회신 대기**

- **동료 B**(교육팀) — 미팅 일정 택일 요청(9/8 또는 9/9), 이틀째 대기
- **Viva Insights** 추가 확인 사항 — 요청 내용 확인 필요
- **고객사 B** SharePoint 링크 회신 대기

**이번 주 기한**

- 워크숍 주차 사전 등록
- 영업 시스템 회계연도 목표 확인
- 9/8 지방 사업장 교육 자료 확정

근거: 오늘 캘린더, 최근 메일. 확인되지 않은 항목은 '확인 필요'로 적었습니다."""

FINAL_REAL = """오늘 아침 브리핑을 본인 Teams 채팅으로 보냈습니다.

요약하면:

- **회의 4건** — 08:00 사내 기술 세션 시리즈(Option 2), 10:00 도입 프로그램 리프레셔 L300(두 건 시간 겹침), 12:30 지역 커뮤니티 콜, 17:30 워크숍 준비(동료 A)
- **회신 대기** — 동료 B(교육팀)의 미팅 일정 택일 요청(9/8 또는 9/9)이 가장 급하고, Viva Insights 추가 확인 사항, 고객사 B SharePoint 링크 회신 대기
- **이번 주 기한** — 워크숍 주차 사전 등록, 영업 시스템 회계연도 목표 확인, 9/8 지방 사업장 교육 자료 확정

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
     'target': '☀️ 오늘의 브리핑 — 9월 3일(목) 오늘 회의 • 08:00–11:00 사내 기술 세션…',
     'status': '메시지를 만드는 중', 'act': 'Teams 메시지를 준비하는 중'},

    {'t': 'mail', 'chat': True, 'time': '오후 12:36',
     'to': 'me', 'body': BRIEF_REAL,
     'status': '요청 작업 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'approved', 'time': '오후 12:36', 'label': '1개 작업 승인됨',
     'status': '메시지를 보내는 중'},

    {'t': 'final', 'time': '오후 12:36', 'body': FINAL_REAL,
     'status': '완료', 'act': '작업 완료'},
]


# ── 데모 테넌트 회차 ──────────────────────────────────────
T_DEMO_1 = ('Calendar returns nothing for today. That is not a lookup failure, the day is simply '
            'empty. Mail has two items that look like they want a decision, and neither states a '
            'reply deadline. Teams search comes back with nothing.')
T_DEMO_2 = ('Two of the three sections have no confirmed content. I will say so plainly rather '
            'than stretch the mail items into filler. Where a reply deadline is not stated in the '
            'message, I mark it 확인 필요 instead of guessing one.')

BRIEF_DEMO = """**오늘의 브리핑 — 9월 3일 (목)**

**1. 오늘 회의**

- 등록된 일정 없음 (오늘 캘린더 비어 있음)

**2. 답을 기다리는 급한 메일**

- **심사 대응 자료 검토 요청 — 10월 12일 ISMS-P 사후심사** (Copilot User, 9/2)
  검토 요청 상태, 미읽음. 경영진 판단이 필요한 미비 항목 3건 중 R-001(공용 관리자 계정 14개 잔존)은 목표일 9/30, R-002는 고객 개인신용정보 Azure Blob 컨테이너 3개 암호화 미적용.
  → 회신 필요 여부·기한은 메일에 명시되지 않음(확인 필요)
- **사업장 출입 – 출입증 미태그 상위 10명** (Copilot User, 9/2, 미읽음)
  퇴근 태그 누락 164건(27.3%), 12명 전원 발생. 회신 요청 문구는 확인되지 않음(확인 필요)
- 나머지는 자동 다이제스트 메일로 회신 불필요

**3. 이번 주 기한 있는 일**

- 이번 주(9/3~9/6) 마감으로 확인된 항목 없음
- 참고 — 다가오는 기한: R-001 조치 목표일 9/30, ISMS-P 사후심사 10/12~16

근거: 오늘 캘린더, 최근 메일(8/25 이후). Teams 채팅은 조회 결과 없음."""

LOG_DEMO = [
    {'t': 'think', 'label': '사고 과정', 'time': '오후 12:32', 'body': T_SCHED,
     'status': '되풀이 작업으로 만드는 중'},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 12:32', 'body': T_RULE,
     'status': '규칙을 문장으로 옮기는 중'},

    {'t': 'tool', 'icon': 'clock', 'label': '되풀이 작업 만들기', 'time': '오후 12:32',
     'status': '예약을 준비하는 중', 'act': '되풀이 작업을 만드는 중'},

    {'t': 'schedule', 'time': '오후 12:32',
     'name': '평일 아침 브리핑', 'every': '평일', 'at': '오전 7:30', 'where': '새 대화',
     'desc': DESC_DEMO,
     'status': '예약 승인을 기다리는 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'approved', 'time': '오후 12:33', 'label': '1개 작업 승인됨',
     'status': '예약을 등록하는 중'},

    {'t': 'prompt', 'time': '오후 12:33', 'sep': '지금 한 번 실행', 'body': DESC_DEMO},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 12:34',
     'status': '단계를 추적하는 중', 'act': '일정과 메일을 조회하는 중',
     'items': [
         {'think': True, 'body': T_DEMO_1},
         {'icon': 'cal', 'tag': 'Outlook', 'label': '일정 보기', 'target': '오늘'},
         {'icon': 'mail', 'tag': 'Outlook', 'label': '메시지 나열', 'target': '최근 메일'},
         {'icon': 'teams', 'tag': 'Teams', 'label': '채팅 나열'},
         {'think': True, 'body': T_DEMO_2},
     ]},

    {'t': 'tool', 'icon': 'teams', 'tag': 'Teams', 'time': '오후 12:36',
     'label': 'Teams 메시지 보내는 중:',
     'target': '오늘의 브리핑 — 9월 3일 (목) 1. 오늘 회의 • 등록된 일정 없음…',
     'status': '메시지를 만드는 중', 'act': 'Teams 메시지를 준비하는 중'},

    {'t': 'mail', 'chat': True, 'time': '오후 12:36',
     'to': 'me', 'body': BRIEF_DEMO,
     'status': '요청 작업 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'cut', 'time': '오후 12:36',
     'body': '실제 기록은 여기까지입니다. 승인 대기 상태로 멈춰 있습니다.'},
]


def build(rid, chat_title, subtitle, note, sched_name, log, tools):
    return {
        'id': rid,
        'tc': '실습-04',
        'folder': '실습',
        'title': '평일 아침 브리핑 자동화',
        'chatTitle': chat_title,
        'subtitle': subtitle,
        'model': '자동',
        'effort': '보통',
        'date': '2026년 9월 3일 목요일',
        'credit': None,
        'note': note,
        'scheduled': {
            'name': sched_name,
            'when': 'Every week on Monday, Tuesday, Wednesday, Thursday, Friday at 07:30',
        },
        'bench': BENCH,
        'steps': [],
        'skills': [],
        'tools': tools,
        'prompt': PROMPT,
        'promptTime': '오후 12:31' if rid == 'brief-real' else '오후 12:32',
        'log': log,
        'artifacts': [],
    }


runs = [
    build('brief-real', '평일 아침 브리핑 · 일정 있는 계정',
          '짧은 요청을 상세 작업 설명으로 늘려 평일 오전 7시 30분 되풀이 작업으로 남긴 실행. '
          '회의 4건과 회신 대기 3건을 찾아 한 화면에 담았다',
          '근거가 없는 준비물은 채우지 않고 확인 필요로 남깁니다.',
          '평일 아침 브리핑 (Teams)', LOG_REAL, ['일정', 'Outlook', 'Teams']),

    build('brief-demo', '평일 아침 브리핑 · 일정 없는 계정',
          '같은 프롬프트를 캘린더가 빈 계정에서 돌린 실행. 없는 일정을 지어내지 않고 '
          '없다고 적었다',
          '찾을 게 없으면 없다고 적습니다. 빈 자리를 메우지 않습니다.',
          '평일 아침 브리핑', LOG_DEMO, ['일정', 'Outlook', 'Teams']),
]

for r in runs:
    p = os.path.join(RUNS, r['id'] + '.json')
    json.dump(r, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%-12s 로그 %2d단계' % (r['id'], len(r['log'])))
