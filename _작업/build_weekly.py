# -*- coding: utf-8 -*-
"""실습-05 사내 표준 서식으로 주간 업무보고 만들기.

실습-02(출입기록)와 실습-03(ISMS-P)에서 만든 것이 그대로 이 주의 업무가 된다.
앞 실습의 산출물이 다음 실습의 입력이 되는 마지막 고리다.

두 번째 커스텀 스킬(company-template)이 등장한다. 서식 파일을 함께 들고 있어
매번 같은 모양이 나오게 한다.

보고서 본문은 데모 테넌트의 한 주를 준법감시팀 한 팀의 업무로 각색했다.
바꾸지 않은 것: 크레딧 271, 단계 4개, 도구 6종, 시각, 「확인 필요」 처리 방식.
"""
import json
import os

import ladder

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'runs', 'weekly-team.json')

PROMPT = """지난 7일간 내 메일함(보낸 메일과 받은 메일 모두), Teams 메시지, 캘린더 일정,
내가 편집한 업무 문서를 함께 훑어 주간 업무보고를 만들어 줘.

이렇게 정리해 줘.

받은 메일은 내가 답한 것과 나에게 할 일이 넘어온 것만 본다.

뉴스레터와 시스템 자동 알림, 회의 수락과 거절 메일은 뺀다.

프로젝트별로 묶는다. 어느 프로젝트인지 모호하면 「기타」로 모은다.

프로젝트마다 ①진행 상황 ②이슈와 리스크 ③다음 주 계획 순서로 적는다.

한 항목은 세 줄을 넘기지 않는다.

근거가 된 메일이나 회의는 항목 끝에 날짜와 함께 괄호로 적는다.

아직 답하지 않았는데 답이 필요한 메일은 「미회신」으로 따로 모은다.

「사내 표준 서식」 Skill의 Word 규칙과 표 구조를 그대로 지킨다.

확인되지 않은 것은 지어내지 말고 「확인 필요」로 표시한다.

완성되면 Word 파일로 저장하고, 핵심 내용 세 줄 요약을 Teams 메시지로 나에게 보내 줘."""

T1 = ('Two skills are in play. korean-proofread is not needed here, but company-template '
      'is: it carries the Word rules and the table structure this report has to follow. '
      'I read the form file first so the report comes out in the house shape, not mine.')
T2 = ('Seven days of mail splits into two real projects and a remainder. The audit thread '
      'and the badge thread each have a clear owner and a deadline. Everything else is '
      'digest mail and site-share notices, which the prompt tells me to drop.')
T3 = ('Calendar and Teams come back empty for the window. I will not pad the report with '
      'invented meetings. The 기타 row gets 확인 필요 and the summary says the evidence base '
      'was mail and edited documents only.')
T4 = ('Two threads are waiting on the user and neither has been answered. They go in the '
      '미회신 section with what the sender actually asked, not my guess at urgency.')

SUMMARY = """주간 업무보고(2026-08-27 ~ 09-03) 세 줄 요약

1. ISMS-P 사후심사 제출 자료 4종을 마무리해 경영진 검토를 요청했고, 사업장 출입기록 600건 점검 결과를 보고했습니다.
2. 가장 급한 것은 R-002 미암호화 컨테이너 3개(목표 9/25)이며, R-001과 R-004도 심사 전 결정이 필요합니다.
3. 다음 주에는 세 건의 결정을 확정할 30분 논의 자리를 잡는 일이 가장 중요합니다."""

FINAL = """주간 업무보고를 만들어 저장하고, 세 줄 요약도 Teams로 보내 드렸습니다.

파일: **주간업무보고_2026-08-27_2026-09-03.docx**
사내 표준 서식의 Word 규칙과 표 구조를 그대로 따랐습니다. 머리 표 4칸, 「1. 이번 주 요약」 세 줄, 「2. 프로젝트별 진행」 4열 표. 서식 파일에 들어 있던 작성 규칙 절은 산출물에서 지웠습니다.

**프로젝트별 정리 (3행)**

- **ISMS-P 사후심사 대응** — 제출 자료 4종 작성 완료·검토 요청, 접근통제 정책과 데이터 보존·파기 정책, 심사체크리스트, 위험관리대장 갱신 / 이슈는 R-001 공용 관리자 계정 14개(목표 9/30), R-002 개인신용정보 Azure Blob 컨테이너 3개 미암호화(목표 9/25), R-004 Litware 상시 접근권한 법무 검토 중 (9/2 검토 요청 메일, 9/2 정책 문서 편집)
- **사업장 출입기록 점검** — 2026-06-01~08-20 출입기록 600건 점검, 퇴근 태그 누락 164건(27.3%) 보고. 12명 전원에게서 누락이 발생했고 그중 3명은 누락 비율이 절반을 넘습니다 (9/2 메일 2건)
- **기타** — 사내 표준 서식 자료 정리, Communication site 초대 수신

**미회신 2건**은 별도 절로 모았습니다. 심사 대응 자료 검토 회신과 논의 일정 확정, 출입기록 후속 조치 주체 지정입니다.

**확인 필요로 표시한 것**

- 부서명이 프로필에서 확인되지 않아 「확인 필요」로 두었습니다
- 지난 7일 캘린더 일정과 Teams 메시지가 조회되지 않아 「기타」 이슈 칸에 「확인 필요」로 적었습니다. 근거는 메일과 편집한 문서만 사용했습니다
- 뉴스레터(Entra·PIM·메시지 센터 다이제스트)와 사이트 공유 알림은 본문 근거에서 제외했습니다"""

LOG = [
    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 2:04',
     'status': '단계를 계획하는 중', 'act': '사내 표준 서식을 확인하는 중',
     'items': [
         {'think': True, 'body': T1},
         {'icon': 'newfile', 'label': '사용자 지정 기술', 'target': 'company-template',
          'tag': '검토 완료'},
         {'icon': 'file', 'tag': 'SharePoint', 'label': '서식 파일 읽기',
          'target': 'weekly-report-form.docx'},
     ]},

    {'t': 'tools', 'label': '지난 7일 자료를 모으는 중', 'time': '오후 2:05',
     'status': '메일과 문서를 훑는 중', 'act': '지난 7일 자료를 수집하는 중',
     'items': [
         {'icon': 'mail', 'tag': 'Outlook', 'label': '메시지 나열', 'target': '보낸 메일 · 받은 메일'},
         {'icon': 'cal', 'tag': '일정', 'label': '일정 보기', 'target': '08-27 ~ 09-03'},
         {'icon': 'search', 'tag': 'Teams', 'label': '프로젝트 검색 중'},
         {'think': True, 'body': T2},
         {'icon': 'web', 'tag': 'Work IQ', 'label': '조직 콘텐츠 검색', 'target': '편집한 문서'},
         {'icon': 'struct', 'tag': 'Microsoft Graph', 'label': '문서 편집 이력 확인'},
     ]},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 2:07', 'body': T3,
     'status': '근거 없는 칸을 가리는 중'},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 2:08', 'body': T4,
     'status': '미회신을 고르는 중'},

    {'t': 'edit', 'time': '오후 2:09', 'file': '주간업무보고_2026-08-27_2026-09-03.docx',
     'kind': 'w', 'status': '보고서를 쓰는 중', 'act': 'Word 문서를 작성하는 중',
     'items': [
         {'k': '서식 적용', 'v': '머리 표 4칸 · 제목 Segoe UI · 강조선', 'size': 4},
         {'k': '1. 이번 주 요약', 'v': '세 줄', 'size': 3},
         {'k': '2. 프로젝트별 진행', 'v': '4열 표 · 3행', 'size': 12},
         {'k': '3. 미회신', 'v': '2건', 'size': 2},
         {'k': '작성 규칙 절 삭제', 'v': '서식 파일에만 있던 안내 문단', 'size': 1},
     ]},

    {'t': 'say', 'time': '오후 2:10', 'body': 'Now publishing the file.',
     'status': '파일을 옮기는 중'},

    {'t': 'tools', 'label': '파일 복사', 'time': '오후 2:10',
     'status': '출력 폴더로 옮기는 중', 'act': '산출물을 저장하는 중',
     'items': [
         {'icon': 'copy', 'label': '파일 복사'},
         {'icon': 'search', 'label': '파일 검색', 'target': 'output/**/*'},
     ]},

    {'t': 'tool', 'icon': 'teams', 'tag': 'Teams', 'time': '오후 2:11',
     'label': 'Teams 메시지 보내는 중:',
     'target': '주간 업무보고(2026-08-27 ~ 09-03) 세 줄 요약 1. ISMS-P 사후심사 제출 자료를…',
     'status': '요약을 보내는 중', 'act': 'Teams 메시지를 준비하는 중'},

    {'t': 'mail', 'chat': True, 'time': '오후 2:11', 'to': 'me', 'body': SUMMARY,
     'status': '승인을 기다리는 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'approved', 'time': '오후 2:11', 'label': '1개 작업 승인됨',
     'status': '메시지를 보내는 중'},

    {'t': 'final', 'time': '오후 2:11', 'body': FINAL,
     'status': '완료', 'act': '작업 완료'},
]

data = {
    'id': 'weekly-team',
    'tc': '실습-05',
    'folder': '실습',
    'title': '사내 표준 서식으로 주간 업무보고',
    'chatTitle': '주간 업무보고 · 사내 표준 서식',
    'subtitle': '앞의 두 실습에서 만든 일이 그대로 이번 주 업무가 된 실행. '
                '두 번째 커스텀 스킬이 서식 파일을 들고 나온다',
    'model': '자동',
    'effort': '보통',
    'date': '2026년 9월 3일 목요일',
    'credit': 271,
    'costTime': '오후 2:11',
    'note': '캘린더와 Teams가 비자 채우지 않고 확인 필요로 남깁니다.',
    'bench': ladder.bench('주간보고 · 사내 표준 서식',
                          '271은 서식을 확인하고 Word 하나를 만든 값입니다.'),
    'steps': [
        '사내 표준 서식 규칙과 양식 파일 확인',
        '지난 7일 메일·Teams·일정·문서 수집',
        '프로젝트별 정리 및 Word 보고서 작성',
        '세 줄 요약 Teams 발송',
    ],
    'skills': ['company-template'],
    'tools': ['일정', 'SharePoint', 'Microsoft Graph', 'Outlook', 'Teams', 'Work IQ'],
    'prompt': PROMPT,
    'promptTime': '오후 2:03',
    'promptFiles': ['weekly-report-form.docx'],
    'log': LOG,
    'artifacts': [
        {'name': '주간업무보고_2026-08-27_2026-09-03.docx', 'kind': 'Word 문서',
         'meta': '1쪽 · 732단어 · 표 2개', 'pages': [], 'labeled': True},
    ],
}

json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('weekly-team.json  로그 %d단계' % len(LOG))
