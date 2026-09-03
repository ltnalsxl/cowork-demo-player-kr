# -*- coding: utf-8 -*-
"""시나리오 다섯 개가 공유하는 값.

크레딧과 실행 정보는 실측이므로 여기서만 관리한다.
"""

# ── TC-04 딥리서치 ───────────────────────────────────────
TC04_PROMPT = (
    '국내 피지컬AI 시장의 최근 12개월 동향을 딥리서치해줘.\n\n'
    '조사 항목:\n'
    '1. 시장 규모와 성장률 (가능하면 복수 출처 교차 검증)\n'
    '2. 주요 경쟁사 5곳의 제품 라인업, 가격 정책, 시장 포지셔닝\n'
    '3. 관련 규제 및 정책 변화\n'
    '4. 주목할 기술 트렌드\n\n'
    '추가로, 우리 회사 SharePoint에 있는 기존 시장분석 자료 및 영업팀 리포트와 대조해서 '
    '"외부에서 보는 시각"과 "사내에서 인식하고 있는 내용" 사이의 갭을 짚어줘.\n\n'
    '산출물:\n'
    '① 20페이지 분량의 Word 보고서 (모든 주장에 출처를 각주로 표기)\n'
    '② 경영진 공유용 요약 PowerPoint 10장'
)

TC04_BENCH = {
    'n': 3, 'people': 1, 'min': 1614, 'max': 2126,
    'condition': '같은 프롬프트, 같은 계정, 같은 데이터로 모델만 바꿔 돌렸습니다. '
                 '회차마다 앞선 결과물을 정리해 서로 영향을 주지 않게 했습니다. '
                 '노력은 모델 기본값입니다.',
    'models': [
        {'name': 'GPT 5.6 Terra', 'avg': 1614, 'n': 1, 'effort': '매우 높음',
         'meta': '87분 · 단계 3 · Word 26,411자 표 6 · PPT 이미지 1'},
        {'name': 'Sonnet 5', 'avg': 2126, 'n': 1, 'effort': '보통',
         'meta': '65분 · 단계 5 · Word 14,664자 표 1 · 편집 실패 14회'},
    ],
}

# ── TC-01 주간 업무보고 ──────────────────────────────────
TC01_PROMPT = (
    '지난 7일간 내 보낸 메일, Teams 메시지, 캘린더 일정, 그리고 내가 편집한 파일을 분석해서 '
    '주간 업무보고를 작성해줘.\n\n'
    '다음 조건을 지켜줘:\n'
    '1. 프로젝트별로 묶어서 정리할 것\n'
    '2. 각 프로젝트마다 ①진행 상황 ②이슈 및 리스크 ③다음 주 계획 순서로 작성\n'
    '3. 각 항목은 3줄 이내로 간결하게\n'
    '4. 근거가 된 메일이나 회의는 항목 끝에 괄호로 표기\n'
    '5. 첨부한 사내 주간보고 양식의 서식과 표 구조를 그대로 유지\n\n'
    '완성되면 Word 파일로 저장하고, 핵심 내용 3줄 요약을 Teams 메시지로 나에게 보내.'
)

TC01_BENCH = {
    'n': 2, 'people': 1, 'min': 219, 'max': 1178,
    'head': '같은 일을 데이터가 다른 계정에서 시키면',
    'lead': '모델과 노력을 고정하고 계정만 바꿔 돌린 실측값입니다.',
    'condition': '모델과 노력을 고정하고 계정만 바꿨습니다. '
                 '한쪽은 메일·회의·대화가 0건인 계정, 다른 쪽은 진행 중인 프로젝트 7건이 있는 계정입니다.',
    'models': [
        {'name': '활동 없는 계정', 'avg': 219, 'n': 1, 'effort': '보통',
         'meta': '데이터 0건 · 표 없음 · 문서 1쪽'},
        {'name': '활동 많은 계정', 'avg': 1178, 'n': 1, 'effort': '보통',
         'meta': '프로젝트 7건 · 표 8개 · 편집 실패 14회 · 문서 3쪽'},
    ],
}

# ── 산출물 ───────────────────────────────────────────────
def art(name, kind, meta, path, pages):
    return {'name': name, 'kind': kind, 'meta': meta,
            'file': 'assets/artifacts/' + path,
            'thumb': 'assets/artifacts/' + pages[0],
            'pages': ['assets/artifacts/' + p for p in pages]}


ART_AUTO = [
    art('국내 피지컬AI 시장 동향 분석 보고서.docx', 'Word 문서', '27쪽 · 표 4개 · 출처 30건',
        '국내 피지컬AI 시장 동향 분석 보고서.docx',
        ['doc_01.png', 'doc_04.png', 'doc_09.png']),
    art('국내 피지컬AI 시장 동향 경영진 브리핑.pptx', 'PowerPoint 프레젠테이션',
        '10장 · 16:9 · 차트 1개 · 표 2개',
        '국내 피지컬AI 시장 동향 경영진 브리핑.pptx',
        ['ppt_%02d.png' % i for i in range(1, 11)]),
]

ART_SONNET = [
    art('국내 피지컬AI 시장 동향 분석 보고서.docx', 'Word 문서', '15쪽 · 표 1개 · 출처 39건',
        'sonnet5/국내 피지컬AI 시장 동향 분석 보고서.docx',
        ['sonnet5/doc_01.png', 'sonnet5/doc_04.png', 'sonnet5/doc_09.png']),
    art('국내 피지컬AI 시장 동향 - 경영진 요약.pptx', 'PowerPoint 프레젠테이션',
        '10장 · 16:9 · 표 1개',
        'sonnet5/국내 피지컬AI 시장 동향 - 경영진 요약.pptx',
        ['sonnet5/ppt_%02d.png' % i for i in range(1, 11)]),
]

ART_TERRA = [
    art('국내 피지컬AI 시장 최근 12개월 동향 심층 분석.docx', 'Word 문서',
        '25쪽 · 표 6개 · 출처 34건',
        'terra/국내 피지컬AI 시장 최근 12개월 동향 심층 분석.docx',
        ['terra/doc_01.png', 'terra/doc_04.png', 'terra/doc_09.png']),
    art('국내 피지컬AI 시장 최근 12개월 경영진 요약.pptx', 'PowerPoint 프레젠테이션',
        '10장 · 16:9 · 차트 1개 · 표지 이미지 생성',
        'terra/국내 피지컬AI 시장 최근 12개월 경영진 요약.pptx',
        ['terra/ppt_%02d.png' % i for i in range(1, 11)]),
]

ART_TC01 = [
    art('주간업무보고_2026-08-26_09-02.docx', 'Word 문서', '3쪽 · 표 8개 · 빈 셀 15개',
        'tc01/주간업무보고.docx',
        ['tc01/doc_01.png', 'tc01/doc_02.png', 'tc01/doc_03.png']),
]

SKILLS_DR = ['깊이 탐구하기', 'Word', 'PowerPoint']
TOOLS_DR = ['SharePoint', 'Web Search', 'Work IQ']


