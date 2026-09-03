# -*- coding: utf-8 -*-
"""실습-07 제안요청서 분석과 제안요약서 작성.

두 턴이다. 먼저 PDF를 읽어 HTML 분석 보고서를 만들고, 그 내용으로
사내 표준 서식 스킬을 불러 PPTX 제안요약서를 만든다.

앞의 실습들과 다른 점은 **만들기 전에 목차를 먼저 보여주고 승인을 받는다**는
것이다. "순서: 만들기 전에 목차를 먼저 보여 줘"가 프롬프트에 있고, 목차 열 장을
표로 내놓은 뒤 사용자가 "이대로 진행"이라고 답할 때까지 기다린다.

근거가 없는 자리는 지어내지 않고 대괄호로 비운다. 회사명, PM 이름, 수행 실적이
제안요청서에 있을 리 없어서다. 일정표는 원문이 도형 막대라 텍스트로 확정할 수
없다고 밝힌다.

원문 제안요청서는 공개 입찰 공고라 기관명을 그대로 둔다.
바꾸지 않은 것: 크레딧 348, 도구, 스킬, 시각, 산출물 이름.
"""
import json
import os

import ladder

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'runs', 'rfp-deck.json')

PDF = 'rfp-public-ai-procurement.pdf'
HTML = '공공AI사업_추진체계_유연화_방안마련_제안요청서_분석보고서.html'
PPTX = '제안요약서_공공AI사업_추진체계_유연화.pptx'

PROMPT1 = """첨부한 제안요청서를 분석해서 HTML 형식의 분석 보고서를 만들어 줘.

결과물: 사업 개요 · 추진 일정 · 평가 배점과 가격 항목 구조 · 유의해야 할 조항과 대응 방향 · 제출 서류 체크리스트

자료: 첨부한 파일만 사용

완료 기준: HTML 파일 한 건을 OneDrive에 저장

제약: 각 항목을 순서대로 진행하고 추측이 필요한 곳은 지어내지 말고 표시해 줘.

승인 범위: 추가 정보가 꼭 필요하면 나에게 물어보고 진행해."""

PROMPT2 = """등록한 「사내 표준 서식」 Skill을 써서, HTML 분석 보고서 내용으로 제안요약서를 만들어 줘.

목차: 평가 배점표의 항목 순서를 그대로 따라 줘.

분량: 10장 안쪽

순서: 만들기 전에 목차를 먼저 보여 줘."""

T1 = ('The prompt names five sections and says to work through them in order. '
      'It also says not to invent anything that needs guessing. Two places in this '
      'document will trip that: the schedule chart is drawn as bars with no month '
      'labels in the text layer, and the submission list defers to a notice I do not have.')

T2 = ('A proposal summary is presentation material, so the PowerPoint template is the '
      'right half of the house style, not the Word one. I read company-template first '
      'to see which layouts exist before deciding how to split ten slides.')

T3 = ('The scoring table has eight line items adding to 100. If I follow that order and '
      'give more slides to the heavier items, the deck maps one-to-one onto how the '
      'evaluators will read it. Company profile and PM history are not in the RFP, so '
      'those stay as bracketed blanks.')

FINAL1 = """분석 보고서를 만들어 OneDrive에 저장했습니다. 요청하신 다섯 항목을 순서대로 담았습니다.

- **사업 개요** — 사업명, 예산 70,000,000원(부가세 포함), 기간 계약체결일~180일, 추진 배경 3대 한계점, 주관·발주·수행사 역할, 과업 3대 축과 정량 요건(유형 5개 이상, 전문가 10명 이상, 유형별 사례 3건 이상)
- **추진 일정** — M~M+5 상대 일정 기준 과업 목록과 보고 체계(주간·중간·종료)
- **평가 배점과 가격 항목 구조** — 기술 90% + 가격 10%, 기술평가 100점 세부 배점표 전체, 85% 미만 배제 기준, 입찰가격 평점 근거, 상생협력 지분율 평점표
- **유의 조항과 대응 방향** — 15개 조항을 원문 요지와 대응 방향 대비표로 정리(소기업·소상공인 자격, 업종코드 1169, 공동이행방식 지분 설계, PM 불참 시 서면평가, 지재권 공동소유, 제안서의 계약조건화)
- **제출 서류 체크리스트** — 제안서류 본체, 자격 서류, 공동수급, 제안서 목차 구성 요건

**추측이 필요한 곳은 지어내지 않고 표시했습니다.** 두 가지를 확인하셔야 합니다.

1. **추진 일정표** — 원문 2쪽 일정표는 각 과업의 배치가 도형 막대로만 표시돼 있어 과업별 시작·종료 월을 텍스트로 확정할 수 없습니다. 임의로 배치하지 않고 과업 목록만 옮긴 뒤 원문 확인을 권고해 두었습니다.
2. **제출 서류 목록** — 원문 Ⅳ-5는 제출서류, 제출 일정, 평가를 모두 "입찰공고문 참조"로만 규정합니다. 공식 목록이 이 문서에 없어서, 체크리스트는 본문에서 명시적으로 확인되는 요건만 담았습니다.

발주기관 확인이 필요한 항목(상생협력 평점의 총점 반영 방식, 조달 일정, 산출물 부수와 대가 지급 조건)도 문의처와 함께 정리해 두었습니다. 입찰공고문을 주시면 체크리스트를 완성본으로 보강하겠습니다."""

TOC = """제안요약서는 제안서 발표자료이므로 사내 표준 서식 중 PowerPoint 템플릿(`company-template.potx`)으로 만들겠습니다. 만들기 전에 목차부터 보여드립니다.

**제안요약서 목차(안) — 총 10장**

목차는 제안요청서 Ⅳ-3-나 기술평가 배점표에 적힌 항목 순서 그대로 뽑았고, 배점이 큰 항목에 장을 더 배분했습니다.

| # | 장 제목 | 배점 | 레이아웃 |
| --- | --- | --- | --- |
| 1 | 「공공 AI사업 추진체계 유연화 방안 마련」 제안요약서 | — | 표지 |
| 2 | 일반현황 — 제안사·조직·수행체계 | 20 | 제목과 본문 |
| 3 | 사업 이해도와 추진전략 | 20 | 2단 본문 |
| 4 | 사업 방법론 | 10 | 제목과 본문 |
| 5 | 공공 AI 사업 유형화 및 유연화 적용 과제 선정 | 10 | 제목과 본문 |
| 6 | 공공 AI 사업 추진체계 재설계 | 10 | 2단 본문 |
| 7 | 법·제도 개선안 마련 | 10 | 제목과 본문 |
| 8 | 프로젝트 관리 — 관리방법론·관리역량·일정계획 | 15 | 표 한 판 |
| 9 | 보안관리방안과 사회적 가치·안전 관리 | 5 | 제목과 본문 |
| 10 | 마무리 | — | 마무리 |

**배점 대응 확인**: 20 + 20 + 10 + 10 + 10 + 10 + 15 + 5 = 100점 전 항목을 덮습니다.

**미리 알려드릴 점** — 2장 일반현황, 4장의 적용 경험, 8장의 PM 경력은 제안요청서와 분석 보고서에 근거 자료가 없습니다. 회사명, 인원수, 실적, PM 이름을 지어내지 않고 `[제안사명]`, `[PM 성명·경력]` 같은 자리 표시로 비워 두고 채우실 곳을 슬라이드에 표시하겠습니다."""

FINAL2 = """승인하신 목차대로 제안요약서를 만들었습니다.

**만든 내용**

- 총 10장(표지·마무리 포함), 사내 표준 서식 `company-template.potx` 사용
- 쓴 레이아웃: 표지 1장, 제목과 본문 5장, 2단 본문 2장, 표 한 판 1장, 마무리 1장
- 8장의 프로젝트 관리 표는 4열 × 7행(머리 행 포함), 왼쪽 0.72" · 위 1.74" · 너비 11.89"에 배치했고 셀 색과 테두리는 지정하지 않아 템플릿 서식을 그대로 상속받게 두었습니다
- 글자 크기, 색, 글꼴은 슬라이드에서 손대지 않았고 본문은 두 수준까지만 썼습니다
- 전 슬라이드 렌더링 검사 결과 본문 넘침 없음. 가장 긴 슬라이드도 본문 영역 안에 들어옵니다

**목차와 배점 대응**: 일반현황 20 → 전략 및 방법론 30(3장 분할) → 사업수행 30(3장) → 프로젝트 관리 15 → 보안·사회적 가치 5. 배점표에 적힌 순서 그대로이며 100점 전 항목을 덮습니다.

근거 자료는 첨부하신 제안요청서와 앞서 만든 HTML 분석 보고서만 사용했습니다.

**채워 넣으셔야 할 자리 표시** — 원본에 근거가 없어 지어내지 않고 비워 두었습니다.

- 2장: `[제안사명]`, 설립 `[연도]`, 주요 연혁, 총 인원수와 AI 정책·법제도 연구인력 수
- 4장: `[유사 용역 수행 실적 기재]`
- 8장: `[PM 성명·유사 프로젝트 관리 경력 기재]` — PM은 제안서에 반드시 명시해야 하고 미명시 시 서면평가로 전환됩니다

4장의 산출물 제출시기(M / M+3 / M+5)는 제안요청서 일정표의 막대 배치를 텍스트로 확정할 수 없어 **(제안)** 으로 표시했습니다. 원문 2쪽 일정표를 확인하신 뒤 확정 값을 주시면 반영하겠습니다.

템플릿에 들어 있는 「Zava」 로고와 꼬리말은 실습용 예시 브랜드입니다. 실제 제출 전에 마스터의 로고와 꼬리말을 사내 것으로 교체하셔야 합니다."""

log = [
    {'t': 'say', 'time': '오후 10:50',
     'body': 'PDF 본문을 모두 읽었습니다. 이제 분석 보고서를 만들겠습니다.',
     'status': '원문을 읽는 중'},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 10:50', 'body': T1,
     'status': '확정할 수 없는 자리를 가리는 중'},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 10:51',
     'status': '보고서를 쓰는 중', 'act': 'HTML 보고서를 만드는 중',
     'items': [
         {'icon': 'newfile', 'label': '파일 만들기', 'target': HTML},
         {'icon': 'search', 'label': '파일 검색', 'target': 'output/**/*'},
     ]},

    {'t': 'final', 'time': '오후 10:55', 'body': FINAL1, 'out': [0],
     'status': '완료', 'act': '작업 완료'},

    {'t': 'prompt', 'time': '오후 10:56', 'sep': '오후 10:56', 'body': PROMPT2},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 10:56', 'body': T2,
     'status': '어느 서식을 쓸지 정하는 중'},

    {'t': 'tool', 'icon': 'newfile', 'label': '사용자 지정 기술', 'target': 'Company template',
     'tag': '검토 완료', 'time': '오후 10:57',
     'status': '스킬 지침을 읽는 중', 'act': '사내 표준 서식을 확인하는 중'},

    {'t': 'think', 'label': '사고 과정', 'time': '오후 10:57', 'body': T3,
     'status': '목차를 짜는 중'},

    {'t': 'say', 'time': '오후 10:58', 'body': TOC,
     'status': '목차 승인을 기다리는 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'confirm', 'time': '오후 10:59', 'icon': 'newfile',
     'title': '위 10장 목차대로 제안요약서를 만들까요?',
     'rows': [
         ['서식', 'company-template.potx (PowerPoint)'],
         ['분량', '10장 (표지·마무리 포함)'],
         ['목차 기준', '기술평가 배점표 항목 순서'],
     ],
     'note': '근거가 없는 자리는 대괄호로 비워 둡니다.',
     'ok': '이대로 진행',
     'status': '승인을 기다리는 중', 'act': '사용자 승인을 기다리는 중'},

    {'t': 'approved', 'time': '오후 11:00', 'label': '1개 작업 승인됨',
     'status': '제안요약서를 만드는 중'},

    {'t': 'say', 'time': '오후 11:00',
     'body': '승인 감사합니다. 템플릿 레이아웃을 확인하고 만들겠습니다.',
     'status': '레이아웃을 확인하는 중'},

    {'t': 'tools', 'label': '작업을 실행하는 중...', 'time': '오후 11:01',
     'status': '슬라이드를 만드는 중', 'act': 'PowerPoint 파일을 작성하는 중',
     'items': [
         {'icon': 'struct', 'label': '템플릿 레이아웃 확인', 'target': 'company-template.potx'},
         {'icon': 'newfile', 'label': '파일 만들기', 'target': PPTX},
         {'icon': 'file', 'label': '슬라이드 10장 작성'},
         {'icon': 'check', 'label': '렌더링 검사', 'target': '본문 넘침 없음'},
     ]},

    {'t': 'final', 'time': '오후 11:05', 'body': FINAL2, 'out': [1],
     'status': '완료', 'act': '작업 완료'},
]

data = {
    'id': 'rfp-deck',
    'tc': '실습-07',
    'folder': '실습',
    'title': '제안요청서 분석과 제안요약서 작성',
    'chatTitle': '제안요청서 분석 · 제안요약서',
    'subtitle': '제안요청서를 읽어 HTML 보고서를 만들고, 그 내용으로 사내 표준 서식 '
                '제안요약서를 만든 실행. 만들기 전에 목차 열 장을 먼저 보여주고 승인을 받았다',
    'model': '자동',
    'effort': '보통',
    'date': '2026년 9월 3일 목요일',
    'credit': 348,
    'costTime': '오후 11:06',
    'note': '근거가 없는 자리는 지어내지 않고 대괄호로 비웁니다.',
    'bench': ladder.bench('제안요청서 분석 · 제안요약서',
                          '348은 두 턴을 합친 값입니다. '
                          'HTML 보고서 하나와 PPTX 열 장을 만들었습니다.'),
    'steps': [],
    'skills': ['company-template'],
    'tools': ['SharePoint'],
    'prompt': PROMPT1,
    'promptTime': '오후 10:49',
    'promptFiles': [PDF],
    'log': log,
    'artifacts': [
        {'name': HTML, 'kind': 'HTML 파일', 'meta': '5개 절 · 배점표 · 조항 15건', 'pages': []},
        {'name': PPTX, 'kind': 'PowerPoint 프레젠테이션',
         'meta': '10장 · 사내 표준 서식', 'pages': []},
    ],
}

json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('rfp-deck.json  로그 %d단계  크레딧 %d' % (len(log), data['credit']))
