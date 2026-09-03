# -*- coding: utf-8 -*-
"""실습-05 커스텀 스킬을 넣고 그 스킬로 시키기.

앞의 회차들은 모두 대화 안에서 끝났다. 이 회차는 대화 밖에서 시작한다.
스킬 파일을 올리고, 슬래시로 불러, 그 지침대로 교열시킨다.

설치 단계는 캡처를 붙이지 않고 화면을 다시 그렸다. 클릭한 자리에 붉은 테두리가 간다.
"""
import json
import os

from proofread_variants import VARIANTS

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'runs', 'skill-proofread.json')

SKILL_DESC = ('회사에서 쓰는 한국어 문서를 두 축으로 다듬는 교열 스킬. '
              '(1) 회사 문서답게 정확하게: 국립국어원 어문 규범과 공공언...')

# 설치 화면에 실제로 떠 있던 다른 스킬들. 테넌트에 이미 깔려 있던 것이라 그대로 둔다.
MINE = [
    {'n': 'Dynamics 365 ERP Business Operations Router',
     's': 'Routes business-operation requests to Dynamics 365 ERP tools when they concern…'},
    {'n': 'Dynamics 365 Sales',
     's': 'The Dynamics 365 Sales data-access skill — looks up and reports Sales records…'},
    {'n': 'Activity Synthesis',
     's': 'Builds one interpreted, deduplicated engagement view for a sales record…'},
]
BUILTIN = [
    {'n': 'PDF', 's': 'Read, create, and manipulate PDF documents'},
    {'n': 'Word', 's': 'Read, create, and edit Word documents'},
    {'n': 'Excel', 's': 'Read, create, and manipulate Excel spreadsheets'},
]

SKILL_BODY = """당신은 국립국어원 어문 규범과 공공언어 감수 기준을 숙지한 한국어 교열 전문가다. 목적은 두 가지다. **회사 문서답게 정확하게** 다듬고, 동시에 **AI가 쓴 티가 나지 않게** 자연스러운 한국어로 만든다.

**0. 언제 쓰나**

- 사용자가 한국어 텍스트의 "맞춤법, 문법, 띄어쓰기, 교열, 검수, 윤문, 가독성, 표기, 문체, AI 티 제거"를 요청할 때
- 한글 산출물을 만든 뒤 출고 전 최종 점검으로 적용한다
- 대상이 불명확하면 무엇을, 어떤 문체로, 누구를 위한 글인지 먼저 확인한다
- 한국어가 아니면 "한국어 텍스트만 처리합니다"를 안내하고 종료한다

**1. 대상 읽어 오기**

| 대상 | 방법 |
| --- | --- |
| 붙여넣은 텍스트 | 그대로 원문으로 삼는다 |
| 첨부한 Word 문서 | Word 스킬로 본문을 읽는다 |
| 첨부한 PowerPoint | PowerPoint 스킬로 슬라이드별 텍스트를 읽는다 |
| 첨부한 Excel | Excel 스킬로 대상 열이나 시트를 읽는다 |
| OneDrive나 SharePoint 파일 | 파일을 지정받아 읽는다 |"""

NOTICE = """📢 차세대 재고관리 시스템 오픈 안내: 새로운 도약의 시작

안녕하세요, 임직원 여러분. IT지원팀입니다.

금번 프로젝트를 통해 준비되어진 차세대 재고관리 시스템이 — 오랜 준비 끝에 — 드디어 3월 2일 오픈하게 되었음을 안내드리게 되었습니다. 이는 우리 회사의 디지털 전환에 있어 매우 중요한 신호탄이며, 시사하는 바가 크다고 하겠습니다.

이번 오픈의 핵심 사항은 크게 세 가지로 나눌 수 있습니다.

• 데이터 이관: 기존 데이터는 2월 20일부터 2월 28일까지 IT지원팀에 의해 순차적으로 이관되어질 예정입니다. • 서비스 제한: 해당 기간 중 재고 조회 · 입출고 등록 · 리포트 출력 기능이 제한되어질 수 있음을 참고 부탁드립니다. • 사용자 교육: 교육 일정에 대해서는 추후 별도로 공지드릴 예정에 있습니다.

또한 본 시스템의 가장 큰 특징은 실시간으로 재고 현황을 확인할 수 있습니다. 기존 대비 획기적인 처리 속도를 가지고 있으며, 이를 통해 업무 효율성이 극대화되어질 것으로 기대되어집니다. 단순한 시스템 교체가 아니라, 일하는 방식 자체의 혁신적 변화입니다.

따라서 임직원 여러분의 많은 관심과 협조를 부탁드립니다. 결론적으로 이번 오픈은 우리 모두가 함께 만들어가야 하는 여정이라는 것입니다.

※ 문의사항이 있으실 경우 IT지원팀으로 연락 주시기 바랍니다. 🙏"""

PROMPT = '/korean-proofread 아래 사내 공지를 교열해 주세요.\n\n' + NOTICE


def stage(n, cap, screen, note=None, time='오후 1:05'):
    d = {'t': 'stage', 'n': n, 'cap': cap, 'screen': screen, 'time': time,
         'status': '스킬을 넣는 중', 'act': '커스텀 스킬을 설치하는 중'}
    if note:
        d['note'] = note
    return d


INSTALL = [
    stage(1, '왼쪽 사이드바에서 사용자 지정을 연다',
          {'nav': '사용자 지정', 'hl': 'nav', 'title': '사용자 지정',
           'act': '플러그인 추가',
           'tabs': [{'t': '플러그인', 'on': True}, {'t': '기술'}],
           'desc': '플러그인을 사용하면 외부 도구, 서비스, 번들된 기술에 연결해 '
                   'Cowork의 기능을 확장할 수 있습니다.',
           'secs': [{'h': '설치됨', 'd': 'Cowork는 관련 작업에 대해 사용하도록 설정된 플러그인을 참조합니다.',
                     'rows': [{'n': 'Dynamics 365 Sales'}, {'n': 'Dynamics 365 ERP 앱'},
                              {'n': 'Dynamics 365 Customer Service'}]}]},
          '플러그인과 기술은 다른 것이다. 플러그인은 외부 도구에 연결하고, '
          '기술은 일하는 방법을 가르친다.'),

    stage(2, '기술 탭으로 넘어간다',
          {'nav': '사용자 지정', 'title': '사용자 지정', 'act': '추가',
           'tabs': [{'t': '플러그인'}, {'t': '기술', 'on': True, 'hl': True}],
           'desc': '기술은 Cowork에게 특정 작업을 수행하는 방법을 가르칩니다.',
           'secs': [{'h': '내 기술', 'd': 'Cowork는 관련 작업에 대해 사용하도록 설정된 기술을 참조합니다.',
                     'rows': MINE},
                    {'h': '기본 제공', 'd': 'Cowork에 포함된 기술입니다. 이 기술은 비활성화할 수 없습니다.',
                     'rows': BUILTIN}]}),

    stage(3, '오른쪽 위 추가를 누른다',
          {'nav': '사용자 지정', 'title': '사용자 지정', 'act': '추가', 'hl': 'act',
           'tabs': [{'t': '플러그인'}, {'t': '기술', 'on': True}],
           'desc': '기술은 Cowork에게 특정 작업을 수행하는 방법을 가르칩니다.',
           'secs': [{'h': '내 기술', 'rows': MINE}],
           'menu': ['새 기술', '기술 업로드'], 'menuHl': 1},
          '새 기술은 화면에서 직접 쓰는 것이고, 기술 업로드는 만들어 둔 파일을 올리는 것이다.'),

    stage(4, '기술 추가 창이 뜬다',
          {'nav': '사용자 지정', 'title': '사용자 지정',
           'tabs': [{'t': '플러그인'}, {'t': '기술', 'on': True}],
           'secs': [{'h': '내 기술', 'rows': MINE}],
           'modal': {'title': '기술 추가'}},
          '받는 형식은 .MD, .ZIP, .SKILL 셋이다. 참고 파일이 딸린 스킬은 폴더째 압축해 올린다.'),

    stage(5, '만들어 둔 스킬 압축 파일을 고른다',
          {'nav': '사용자 지정', 'title': '사용자 지정',
           'tabs': [{'t': '플러그인'}, {'t': '기술', 'on': True}],
           'secs': [{'h': '내 기술', 'rows': MINE}],
           'modal': {'title': '기술 추가', 'file': 'skill-korean-proofread.zip'}}),

    stage(6, '내 기술 맨 위에 들어온다',
          {'nav': '사용자 지정', 'title': '사용자 지정', 'act': '추가',
           'tabs': [{'t': '플러그인'}, {'t': '기술', 'on': True}],
           'desc': '기술은 Cowork에게 특정 작업을 수행하는 방법을 가르칩니다.',
           'secs': [{'h': '내 기술', 'd': 'Cowork는 관련 작업에 대해 사용하도록 설정된 기술을 참조합니다.',
                     'rows': [{'n': 'korean-proofread', 's': SKILL_DESC, 'hl': True}] + MINE[:2]},
                    {'h': '기본 제공', 'rows': BUILTIN}]}),

    stage(7, '눌러서 안내를 확인한다',
          {'nav': '사용자 지정', 'title': 'korean-proofread',
           'desc': SKILL_DESC, 'body': SKILL_BODY},
          '스킬은 결국 지침 문서다. 화면에서 그대로 읽히고, 고칠 수도 있다.'),

    stage(8, '올린 파일은 내 OneDrive에 그대로 남는다',
          {'crumb': ['내 파일', '문서', 'Cowork', 'skills', 'korean-proofread'],
           'rows': [{'ic': 'folder', 'n': 'references', 'meta': '4개 항목'},
                    {'ic': 'file', 'n': 'README.md', 'meta': '5.00KB'},
                    {'ic': 'file', 'n': 'SKILL.md', 'meta': '9.45KB'}]},
          '숨은 저장소가 아니라 내 OneDrive 폴더다. 파일을 고치면 스킬이 따라 바뀐다.'),
]

T1 = ('The user typed the skill name as a slash command, so the instruction file is loaded '
      'before anything else. It tells me to keep the original text intact and only touch '
      'wording, and to list what changed rather than hand back a silent rewrite.')
T2 = ('The skill splits the work in two: 어문 규범 (spelling, spacing, subject-predicate '
      'agreement, honorifics) and AI 티 (double passives, translationese, filler closers, '
      'em-dashes, decorative emoji). This notice has both kinds, so I need the full pass, '
      'not the quick one.')

LOG = INSTALL + [
    {'t': 'tool', 'icon': 'newfile', 'label': '사용자 지정 기술', 'target': 'Korean proofread',
     'tag': '검토 완료', 'time': '오후 1:12',
     'status': '스킬 지침을 읽는 중', 'act': '커스텀 스킬을 불러오는 중'},

    {'t': 'tool', 'icon': 'folder', 'label': '참고 자료 확인', 'time': '오후 1:12',
     'status': '참고 파일을 여는 중', 'act': 'references 폴더를 읽는 중'},

    {'t': 'think', 'label': '생각 중...', 'time': '오후 1:12', 'body': T1,
     'status': '요청을 처리하는 중'},

    {'t': 'think', 'label': '생각 중...', 'time': '오후 1:13', 'body': T2,
     'status': '어느 모드로 볼지 정하는 중'},

    {'t': 'final', 'vary': True, 'time': '오후 1:13', 'body': '',
     'status': '완료', 'act': '작업 완료'},
]

data = {
    'id': 'skill-proofread',
    'tc': '실습-05',
    'folder': '실습',
    'title': '커스텀 스킬 설치와 문서 교열',
    'chatTitle': '사내 공지 교열 · 모델 다섯',
    'subtitle': '스킬 파일을 올려 설치하고 사내 공지를 교열한 실행. '
                '같은 원문을 모델 다섯으로 돌려 답변을 나란히 볼 수 있다',
    'model': 'Sonnet 5',
    'effort': '보통',
    'date': '2026년 9월 3일 목요일',
    'credit': 25,
    'costTime': '오후 1:14',
    'note': '모델 선택기를 눌러 보십시오. 크레딧과 답변이 함께 바뀝니다.',
    'variants': VARIANTS,
    'bench': {
        'n': 5, 'people': 1,
        'min': min(v['credit'] for v in VARIANTS.values()),
        'max': max(v['credit'] for v in VARIANTS.values()),
        'head': '같은 공지를 모델만 바꿔 교열시키면',
        'lead': '스킬과 프롬프트를 고정하고 모델만 바꿔 새 작업으로 다섯 번 돌린 실측값입니다.',
        'condition': '노력은 모델별 기본값을 그대로 뒀습니다. GPT 5.5와 GPT 5.6 Terra는 '
                     '매우 높음이 기본이고 나머지 셋은 보통입니다. '
                     '다섯 번 모두 새 작업에서 같은 원문을 붙여 넣었습니다.',
        'models': [
            {'name': n, 'avg': v['credit'], 'n': 1, 'effort': v['effort'],
             'meta': '등급 %s · %s · 변경 %s' % (v['grade'], v['counts'], v['change'])}
            for n, v in sorted(VARIANTS.items(), key=lambda kv: kv[1]['credit'])
        ],
    },
    'steps': [],
    'skills': ['korean-proofread'],
    'tools': [],
    'prompt': PROMPT,
    'promptTime': '오후 1:12',
    'promptAt': len(INSTALL),
    'log': LOG,
    'artifacts': [],
}

json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('skill-proofread.json  설치 %d단계 + 대화 %d단계'
      % (len(INSTALL), len(LOG) - len(INSTALL)))
