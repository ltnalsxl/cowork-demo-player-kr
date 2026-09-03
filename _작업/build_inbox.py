# -*- coding: utf-8 -*-
"""실습-07 밀린 메일 정리. 같은 프롬프트를 계정 두 곳에서 돌린 회차 쌍.

inbox-demo  데모 테넌트. 2주 치가 20건이라 분류도 초안도 금방 끝난다.
inbox-real  실계정. 2주 치가 400건이고 걸러 낸 38건을 세 갈래로 나눈다.

195와 755. 읽을 것이 20건에서 400건으로 늘자 3.9배가 됐다.
아침 브리핑(95↔107)이 거의 안 움직인 것과 나란히 놓고 보면,
값을 움직이는 건 '읽을 양 × 만들 것'이라는 게 드러난다.

실계정 회차의 이름, 고객사, 사내 프로그램명은 예시 값으로 바꿨다.
추적표 파일은 민감도 레이블이 걸려 있어 열지 않았고, 건수와 시트 구성만 옮겼다.
바꾸지 않은 것: 크레딧, 단계 구성, 도구, 편집 횟수, 시각.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(BASE, 'runs')

PROMPT = """최근 2주 받은 편지함과 Teams 멘션을 함께 훑어 밀린 메일을 정리해 주세요.

분류: 답을 기다리는 것 / 읽기만 하면 되는 것 / 넘겨도 되는 것

제외: 뉴스레터와 시스템 자동 알림

결과물: Excel 추적표, 답이 필요한 건의 회신 초안(최대 5건)

제약: 회신은 초안에서 멈추고 발송하지 마세요"""

STEPS_DEMO = ['받은 편지함 훑기 (최근 2주)', 'Teams 멘션 확인',
              '분류 및 Excel 추적표 작성', '회신 초안 작성 (최대 5건)']
STEPS_REAL = ['받은 편지함 2주치 검토', 'Teams 멘션·미확인 대화 확인',
              'Excel 추적표 작성', '회신 초안 작성(발송 없음)']


# ── 데모 테넌트 ────────────────────────────────────────────
TD1 = ('Two weeks of inbox comes back at seventeen items, and Teams adds three. '
       'That is small enough to read every one rather than sample. The prompt tells me '
       'to drop newsletters and system notices, so I sort those out first.')
TD2 = ('Only two threads actually ask the user for something. The rest are either the '
       'user\'s own notes or a second copy of a report already counted. I will not pad '
       'the 답을 기다리는 것 column to make the table look fuller.')

FINAL_DEMO = """최근 2주(8/20~9/3) 받은 편지함 17건과 Teams 메시지 3건, 총 20건을 훑었습니다.

추적표: **밀린 메일·Teams 정리 추적표 (2026-08-20~09-03).xlsx** — OneDrive에 저장했습니다. 시트 두 개입니다(「밀린 항목 추적」, 「제외 항목」).

| 분류 | 항목 | 원본 건수 |
| --- | --- | --- |
| 답을 기다리는 것 | 2 | 5 |
| 읽기만 하면 되는 것 | 3 | 4 |
| 넘겨도 되는 것 | 2 | 3 |
| 제외(뉴스레터·자동 알림) | 4 | 8 |

**답을 기다리는 것 (2건)**

- **ISMS-P 사후심사(10/12~16) 대응 자료 검토 요청** — 정다은 준법감시인. R-001·R-002·R-004 세 건의 경영진 결정과 30분 논의 자리를 요청했습니다. R-002(미암호화 Blob 컨테이너 3개)가 목표일 9월 25일로 가장 촉박합니다.
- **출입증 미태그 리포트** — 퇴근 태그 누락 164건(27.3%), 12명 전원 발생, 3명은 미태그 비율 50% 초과. 후속 조치 담당과 기한 지정이 필요합니다.

**읽기만 하면 되는 것 (3건)** — 퇴근 태그 누락 현황 상세 자료, 주간 업무보고 2건(본인 메모)

**넘겨도 되는 것 (2건)** — 미읽음 메일 정리 노트, 출입증 리포트 디자인 변형본(원본과 동일 내용)

**제외** — Entra ID Protection 다이제스트, M365 메시지 센터 주간 업데이트, PIM 다이제스트, SharePoint 사이트 공유 알림

**회신 초안 2건** — 발송하지 않고 초안함에 저장했습니다.

1. ISMS-P 회신: R-002 우선 처리(9/25 유지), R-001 계정별 전환·폐기 확정, R-004 법무 검토 완료 시점 확인 및 한시적 권한 회수 대안, 30분 논의 일정 제안
2. 출입기록 회신: 주관 부서 지정, 상위 대상자 원인 확인(시스템 미인식 vs 절차 미준수), 재발 방지 절차 개선안 — 9/18 회신 요청

답을 기다리는 건이 2건뿐이라 초안도 2건입니다. 참고로 다른 사람이 보낸 Teams 멘션은 없었고, 검색된 Teams 메시지 3건은 모두 본인이 남긴 업무 메모였습니다."""

LOG_DEMO = [
    {'t': 'say', 'time': '오후 2:21', 'body': "I'll start by pulling your recent email and Teams mentions.",
     'status': '자료를 모으는 중'},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 2:22',
     'status': '받은 편지함을 훑는 중', 'act': '최근 2주 메일을 읽는 중',
     'items': [
         {'icon': 'mail', 'tag': 'Outlook', 'label': '메시지 나열', 'target': '08-20 ~ 09-03'},
         {'think': True, 'body': TD1},
         {'icon': 'teams', 'tag': 'Teams', 'label': '멘션 확인'},
         {'icon': 'web', 'tag': 'Work IQ', 'label': '조직 콘텐츠 검색'},
     ]},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 2:23', 'body': TD2,
     'status': '분류를 가리는 중'},

    {'t': 'edit', 'time': '오후 2:24',
     'file': '밀린 메일·Teams 정리 추적표 (2026-08-20~09-03).xlsx', 'kind': 'x',
     'status': '추적표를 만드는 중', 'act': 'Excel 워크북을 쓰는 중',
     'items': [
         {'k': '밀린 항목 추적', 'v': '7행 · 분류 3종', 'size': 7},
         {'k': '제외 항목', 'v': '4행', 'size': 4},
         {'k': '집계 수식', 'v': '분류별 건수', 'size': 3},
     ]},

    {'t': 'say', 'time': '오후 2:24', 'body': "Now verifying the workbook's calculated values.",
     'status': '계산값을 확인하는 중'},

    {'t': 'tool', 'icon': 'check', 'label': '계산값 확인', 'time': '오후 2:24',
     'status': '집계를 검산하는 중', 'act': '수식 결과를 확인하는 중'},

    {'t': 'tool', 'icon': 'pen', 'tag': 'Outlook', 'label': '회신 초안 저장', 'target': '2건',
     'time': '오후 2:25',
     'status': '초안을 저장하는 중', 'act': '회신 초안을 만드는 중'},

    {'t': 'final', 'time': '오후 2:25', 'body': FINAL_DEMO,
     'status': '완료', 'act': '작업 완료'},
]


# ── 실계정 ────────────────────────────────────────────────
TR1 = ('Four hundred messages in two weeks. Reading each one is not the job — sorting is. '
       'I strip the recurring system senders first (expense, leave, internal systems, '
       'training completion, daily digest), which takes the pile down to something a person '
       'could actually act on.')
TR2 = ('Thirty-eight left. The split I care about is whether someone is waiting on a reply, '
       'and a mention in a Teams thread counts as waiting even though there is no mail. '
       'Two of the ten oldest have been sitting for over a week.')
TR3 = ('The workbook needs a summary sheet a person can read in one glance, then three '
       'detail sheets. I will put the counts and a chart on the front sheet so the ten '
       'items that need a reply are visible before anyone scrolls.')
TR4 = ('The prompt caps drafts at five and says not to send. Where a value is the user\'s '
       'to decide — which date, which customer, when they will follow up — I leave a '
       'bracket rather than pick for them.')

FINAL_REAL = """최근 2주(8/21~9/3) 받은 편지함 **400건**과 Teams 대화·멘션을 함께 훑어 정리했습니다. 뉴스레터와 시스템 자동 알림(경비, 휴가, 사내 시스템, 교육 이수, 일일 다이제스트 등)은 제외했고, 남은 **38건**을 세 갈래로 분류했습니다.

추적표: **밀린 메일·Teams 정리 추적표 (2026-08-21~09-03).xlsx** — OneDrive에 저장했습니다. 요약 시트에 분류별 건수와 차트, 나머지 세 시트에 항목별 상세가 들어 있습니다.

| 분류 | 건수 |
| --- | --- |
| ① 답을 기다리는 것 | 10 |
| ② 읽기만 하면 되는 것 | 15 |
| ③ 넘겨도 되는 것 | 13 |

**가장 급한 3건**

- **동료 A** — 고객사 A 담당 임원의 M365 Copilot 교육 문의. 8/21 접수 후 **13일 경과**, 외부 고객이 대기 중입니다.
- **동료 B**(고객사 C 교육팀) — 10/16(금) 확정, 10/27~29 추가 일정, 9/8·9/9 미팅 일정 택일을 오늘 아침에 요청받으셨습니다.
- **동료 C**(고객사 B) — Teams에서 암호화 문서 참조 가능 여부를 물었고, 오늘 새벽 "제품 지원팀과 확인 후 회신드리겠다"고 직접 약속하신 건입니다.

이 밖에 **동료 D** 매니저가 8/27 Teams에서 담당 계정 UAT 등록을 직접 지명해 요청한 건이 **7일째** 남아 있습니다. **동료 E**는 고객사 D 도입 프로그램 정례에서 "사용자 교육"으로 멘션해 사실상 담당 배정 상태입니다.

**회신 초안 5건** — 모두 초안 상태로만 저장했고 발송하지 않았습니다.

1. 동료 A (고객사 A 교육 문의) — 지연 사과 + 확인 항목 3가지
2. 동료 B (고객사 C) — 10/16 확정, 10월 말 일정 확인 예정, 9/8·9/9 중 택일
3. 동료 F (제품 지원팀) — 고객사 B PDF 레이블 추가 확인 2건 전달
4. 동료 E — 고객사 D 사용자 교육 담당 수락 + 확인 항목
5. 동료 G — 업계 서밋 고객 초청 회신

초안에서 대괄호로 남긴 곳(고객사명, 미팅 일자 택일, 확인 예정일)은 직접 정하셔야 하는 값이라 비워 두었습니다. Teams 건 2개(동료 D의 UAT 요청, 동료 C의 문의)는 초안 저장 기능이 없어 추적표에만 담았습니다."""

LOG_REAL = [
    {'t': 'say', 'time': '오후 2:20',
     'body': "I'll start by pulling your inbox and Teams activity from the last two weeks.",
     'status': '자료를 모으는 중'},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 2:21',
     'status': '받은 편지함을 훑는 중', 'act': '2주 치 메일을 읽는 중',
     'items': [
         {'icon': 'mail', 'tag': 'Outlook', 'label': '메시지 나열', 'target': '08-21 ~ 09-03 · 400건'},
         {'think': True, 'body': TR1},
         {'icon': 'mail', 'tag': 'Outlook', 'label': '메일 본문 확인'},
         {'icon': 'teams', 'tag': 'Teams', 'label': '채팅 나열'},
         {'icon': 'teams', 'tag': 'Teams', 'label': '멘션·미확인 대화 확인'},
         {'think': True, 'body': TR2},
     ]},

    {'t': 'say', 'time': '오후 2:22', 'body': "Now I'll build the tracker and the reply drafts.",
     'status': '추적표를 준비하는 중'},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 2:22',
     'status': '워크북을 준비하는 중', 'act': 'Excel 스킬을 부르는 중',
     'items': [
         {'icon': 'newfile', 'label': 'Excel 스프레드시트 작업 준비'},
         {'icon': 'newfile', 'label': '파일 만들기'},
         {'icon': 'struct', 'label': '파일 구조 읽기'},
         {'think': True, 'body': TR3},
         {'icon': 'struct', 'label': '추적표 데이터 정리'},
     ]},

    {'t': 'edit', 'time': '오후 2:23',
     'file': '밀린 메일·Teams 정리 추적표 (2026-08-21~09-03).xlsx', 'kind': 'x',
     'status': '추적표를 만드는 중', 'act': 'Excel 워크북을 쓰는 중',
     'items': [
         {'k': '시트 생성', 'v': '요약 · 답을 기다리는 것 · 읽기만 · 넘겨도 되는 것', 'size': 7},
         {'k': '① 답을 기다리는 것', 'v': '10행 · 보낸 사람·요청 내용·경과일', 'size': 15},
         {'k': '② 읽기만 / ③ 넘겨도 되는 것', 'v': '15행 · 13행', 'size': 22},
     ]},

    {'t': 'say', 'time': '오후 2:24', 'body': 'Now the summary sheet.',
     'status': '요약 시트를 만드는 중'},

    {'t': 'edit', 'time': '오후 2:24',
     'file': '밀린 메일·Teams 정리 추적표 (2026-08-21~09-03).xlsx', 'kind': 'x',
     'status': '요약을 붙이는 중', 'act': '요약 시트를 만드는 중',
     'items': [
         {'k': '분류별 건수', 'v': '10 / 15 / 13', 'size': 4},
         {'k': '차트', 'v': '분류별 막대', 'size': 1},
     ]},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 2:25', 'body': TR4,
     'status': '초안에 남길 빈칸을 정하는 중'},

    {'t': 'say', 'time': '오후 2:25', 'body': 'Now the reply drafts.',
     'status': '초안을 쓰는 중'},

    {'t': 'tool', 'icon': 'pen', 'tag': 'Outlook', 'label': '회신 초안 저장', 'target': '5건',
     'time': '오후 2:26',
     'status': '초안을 저장하는 중', 'act': '회신 초안을 만드는 중'},

    {'t': 'final', 'time': '오후 2:26', 'body': FINAL_REAL,
     'status': '완료', 'act': '작업 완료'},
]

BENCH = {
    'n': 2, 'people': 1, 'min': 195, 'max': 755,
    'head': '같은 정리를 편지함이 다른 계정에서 시키면',
    'lead': '모델과 노력을 고정하고 계정만 바꿔 돌린 실측값입니다.',
    'condition': '모델과 노력을 고정하고 계정만 바꿨습니다. 한쪽은 2주 치가 20건인 계정, '
                 '다른 쪽은 400건인 계정입니다. 둘 다 Excel 추적표 하나와 회신 초안을 만듭니다.',
    'models': [
        {'name': '편지함이 얇은 계정', 'avg': 195, 'n': 1, 'effort': '보통',
         'meta': '20건 → 7건 · 시트 2개 · 초안 2건'},
        {'name': '편지함이 두꺼운 계정', 'avg': 755, 'n': 1, 'effort': '보통',
         'meta': '400건 → 38건 · 시트 4개 · 초안 5건'},
    ],
}


def build(rid, chat_title, subtitle, note, credit, cost_time, steps, tools,
          log, art_name, art_meta):
    return {
        'id': rid,
        'tc': '실습-07',
        'folder': '실습',
        'title': '밀린 메일 정리와 회신 초안',
        'chatTitle': chat_title,
        'subtitle': subtitle,
        'model': '자동',
        'effort': '보통',
        'date': '2026년 9월 3일 목요일',
        'credit': credit,
        'costTime': cost_time,
        'note': note,
        'bench': BENCH,
        'steps': steps,
        'skills': ['Excel'],
        'tools': tools,
        'prompt': PROMPT,
        'promptTime': '오후 2:21' if rid == 'inbox-demo' else '오후 2:20',
        'log': log,
        'artifacts': [
            {'name': art_name, 'kind': 'Excel 스프레드시트', 'meta': art_meta, 'pages': []},
        ],
    }


runs = [
    build('inbox-real', '밀린 메일 정리 · 편지함 400건',
          '2주 치 400건을 훑어 38건으로 걸러 낸 실행. '
          '답을 기다리는 10건을 앞에 세우고 초안 다섯을 발송 없이 남겼다',
          '보낸 사람이 기다린 날수를 세어 오래된 것부터 올립니다.',
          755, '오후 2:27', STEPS_REAL, ['Outlook', 'Teams'], LOG_REAL,
          '밀린 메일·Teams 정리 추적표 (2026-08-21~09-03).xlsx',
          '시트 4개 · 38행 · 차트 1개'),

    build('inbox-demo', '밀린 메일 정리 · 편지함 20건',
          '같은 프롬프트를 2주 치가 20건인 계정에서 돌린 실행. '
          '답이 필요한 게 2건뿐이라 초안도 2건에서 멈췄다',
          '초안 다섯까지 만들 수 있어도 두 건에서 멈춥니다.',
          195, '오후 2:25', STEPS_DEMO, ['Outlook', 'Teams', 'Work IQ'], LOG_DEMO,
          '밀린 메일·Teams 정리 추적표 (2026-08-20~09-03).xlsx',
          '시트 2개 · 7행'),
]

for r in runs:
    p = os.path.join(RUNS, r['id'] + '.json')
    json.dump(r, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%-11s 로그 %2d단계  크레딧 %d' % (r['id'], len(r['log']), r['credit']))
