# -*- coding: utf-8 -*-
"""tc04-sonnet 실행의 경영진 요약 덱을 다시 만든다.

문장, 수치, 출처는 기존 덱에서 그대로 옮긴다. 바꾸는 것은 배치와
글자 크기, 여백뿐이다.

배치 원칙
- 제목은 좌정렬 고정 위치. 본문 시작선은 모든 장에서 같다.
- 본문은 2.00~6.55in 띠 안에 놓고, 블록을 그 띠의 세로 중앙에 맞춘다.
  아래쪽만 뻥 뚫리는 것을 막는다.
- 강조색은 파랑 하나. 위험 신호에만 붉은 톤을 한 번 쓴다.

사용법: python build_sonnet_deck.py
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
OUT = os.path.join(ROOT, 'assets', 'artifacts', 'sonnet5')
NAME = '국내 피지컬AI 시장 동향 - 경영진 요약.pptx'

INK = RGBColor(0x17, 0x18, 0x22)
GRAY = RGBColor(0x5B, 0x5B, 0x66)
MUTE = RGBColor(0x8C, 0x8C, 0x99)
HAIR = RGBColor(0xDF, 0xE3, 0xEE)
BLUE = RGBColor(0x3B, 0x5F, 0xE0)
ROYAL = RGBColor(0x24, 0x33, 0x8F)
NAVY = RGBColor(0x0E, 0x1B, 0x3A)
TINT = RGBColor(0xF4, 0xF6, 0xFD)
BAND = RGBColor(0xEA, 0xEF, 0xFB)
WARN = RGBColor(0xA8, 0x2C, 0x2C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

KO = 'Malgun Gothic'
EN = 'Segoe UI'

M = 0.86
W = 11.61
TITLE_Y = 0.60
Y0 = 2.00          # 본문 띠 위
Y1 = 6.55          # 본문 띠 아래
SRC_Y = 6.86


def band_top(h):
    """블록 높이 h를 본문 띠의 세로 중앙에 맞춘 y좌표."""
    return Y0 + ((Y1 - Y0) - h) / 2.0


def solid(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb


def noline(shape):
    shape.line.fill.background()


def flat(shape):
    noline(shape)
    shape.shadow.inherit = False


def tune(run, size, bold, rgb, font=KO, spc=-20):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = rgb
    f.name = font
    rpr = run._r.get_or_add_rPr()
    rpr.set('spc', str(spc))
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        for old in rpr.findall(qn(tag)):
            rpr.remove(old)
    for tag, face in (('a:latin', font), ('a:ea', KO), ('a:cs', font)):
        rpr.append(rpr.makeelement(qn(tag), {'typeface': face}))


def box(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return s, tf


def para(tf, first, text, size, bold, rgb, font=KO, line=1.25,
         before=0, align=PP_ALIGN.LEFT, spc=-20):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.line_spacing = line
    p.space_after = Pt(0)
    if before:
        p.space_before = Pt(before)
    r = p.add_run()
    r.text = text
    tune(r, size, bold, rgb, font, spc)
    return p


def rule(slide, x, y, w, rgb=HAIR, thick=0.75):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                               Inches(w), Pt(thick))
    solid(s, rgb)
    flat(s)
    return s


def card(slide, x, y, w, h, fill=WHITE, border=HAIR, r=0.035):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = r
    solid(s, fill)
    if border is None:
        noline(s)
    else:
        s.line.color.rgb = border
        s.line.width = Pt(0.75)
    s.shadow.inherit = False
    return s


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def head(slide, title, lead=None, dark=False):
    """제목이 두 줄이면 끊는 자리를 직접 정한다. 마지막 어절만 흘러내리면
    보기 나쁘므로 title에 줄바꿈을 넣어 균형을 맞춘다."""
    _, tf = box(slide, M, TITLE_Y, W, 1.0)
    for i, ln in enumerate(title.split('\n')):
        para(tf, i == 0, ln, 27 if '\n' in title else 28, True,
             WHITE if dark else INK, line=1.18, spc=-30)
    if lead:
        para(tf, False, lead, 15, False, MUTE if dark else GRAY,
             line=1.3, before=9)
    if not dark:
        rule(slide, M, 1.86, W)


def source(slide, text):
    _, tf = box(slide, M, SRC_Y, W, 0.3)
    para(tf, True, text, 9.5, False, MUTE)


def bullets(tf, items, size=14, gap=14, rgb=INK):
    """줄이 넘어가도 둘째 줄이 글머리 아래로 파고들지 않게 내어쓰기를 준다."""
    for i, t in enumerate(items):
        p = para(tf, i == 0, t, size, False, rgb, line=1.42,
                 before=0 if i == 0 else gap)
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', '133350')
        pPr.set('indent', '-133350')
        for tag in ('a:buNone', 'a:buChar', 'a:buFont', 'a:buAutoNum'):
            for old in pPr.findall(qn(tag)):
                pPr.remove(old)
        font = pPr.makeelement(qn('a:buFont'), {'typeface': KO})
        char = pPr.makeelement(qn('a:buChar'), {'char': '·'})
        pPr.append(font)
        pPr.append(char)


def cell_border(cell, edges, rgb, w=6350):
    tcPr = cell._tc.get_or_add_tcPr()
    for e in ('L', 'R', 'T', 'B'):
        for old in tcPr.findall(qn('a:ln%s' % e)):
            tcPr.remove(old)
    for e in edges:
        ln = tcPr.makeelement(qn('a:ln%s' % e), {'w': str(w), 'cap': 'flat'})
        fill = ln.makeelement(qn('a:solidFill'), {})
        fill.append(fill.makeelement(
            qn('a:srgbClr'), {'val': '%02X%02X%02X' % (rgb[0], rgb[1], rgb[2])}))
        ln.append(fill)
        tcPr.append(ln)


def topic_card(slide, x, y, w, h, name, items, accent=BLUE, sub=None,
               size=14):
    """머리에 옅은 띠를 얹은 카드. 안쪽 여백을 넉넉히 준다."""
    card(slide, x, y, w, h)
    hd = 1.02 if sub else 0.82
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.012),
                                   Inches(y + 0.012), Inches(w - 0.024),
                                   Inches(hd))
    solid(strip, TINT)
    flat(strip)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.012),
                                 Inches(y + 0.012), Pt(3), Inches(hd))
    solid(bar, accent)
    flat(bar)
    _, tf = box(slide, x + 0.38, y + 0.06, w - 0.62, hd - 0.12,
                MSO_ANCHOR.MIDDLE)
    para(tf, True, name, 15.5 if size < 14 else 16, True, ROYAL, line=1.22)
    if sub:
        para(tf, False, sub, 12.5, False, GRAY, before=4)
    _, tf = box(slide, x + 0.38, y + hd + 0.32, w - 0.72, h - hd - 0.58)
    bullets(tf, items, size, 13 if size < 14 else 14)


# ---------------------------------------------------------------- 슬라이드
def s01_cover(prs):
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                            prs.slide_width, prs.slide_height)
    solid(bg, NAVY)
    flat(bg)
    wash = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.9), 0,
                              Inches(4.44), prs.slide_height)
    solid(wash, RGBColor(0x11, 0x1F, 0x42))
    flat(wash)

    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(2.62),
                             Inches(0.72), Pt(3.5))
    solid(bar, BLUE)
    flat(bar)

    _, tf = box(s, M, 2.98, 9.6, 2.0)
    para(tf, True, '국내 피지컬AI 시장 동향 보고', 42, True, WHITE,
         line=1.14, spc=-40)
    para(tf, False, '2025.09 – 2026.09 · 경영진 요약', 16, False,
         RGBColor(0xA9, 0xB4, 0xCE), line=1.4, before=18)

    rule(s, M, 6.20, 2.2, RGBColor(0x2C, 0x3A, 0x5E))
    _, tf = box(s, M, 6.44, 9.6, 0.4)
    para(tf, True, '우리 회사 내부 전략 검토용 · 작성: Copilot Cowork',
         11, False, RGBColor(0x76, 0x82, 0xA0))
    return s


def s02_summary(prs):
    s = blank(prs)
    head(s, '실제 성장은 완만하나,\n대기업은 이미 피지컬AI로 전략을 전환하고 있다')

    items = [
        ('시장 규모', '2024년 국내 로봇산업 매출 6조 1,695억원, 전년 대비 3.2% 성장'
                      '(제조업 중심, 여전히 파편화)', BLUE),
        ('경쟁 구도', '현대차·삼성·LG·두산·레인보우로보틱스가 CEO 직속 조직 신설, '
                      '수천억~조원 단위 투자로 재편', BLUE),
        ('정책', 'K-휴머노이드 연합(1조원+ 투자), AI기본법 시행(2026.1) 등 '
                 '정부가 적극 지원 국면', BLUE),
        ('사내 갭', 'SharePoint 전수조사 결과 피지컬AI 관련 시장분석·영업자료 전무, '
                    '인지적 공백 존재', WARN),
    ]
    cw = (W - 0.44) / 2
    ch = 1.94
    y0 = band_top(ch * 2 + 0.34)
    for i, (k, v, accent) in enumerate(items):
        x = M + (i % 2) * (cw + 0.44)
        y = y0 + (i // 2) * (ch + 0.34)
        card(s, x, y, cw, ch)
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.42),
                                 Inches(y + 0.42), Inches(0.46), Pt(3))
        solid(bar, accent)
        flat(bar)
        _, tf = box(s, x + 0.42, y + 0.64, cw - 0.84, 0.4)
        para(tf, True, k, 16, True, ROYAL if accent == BLUE else WARN)
        _, tf = box(s, x + 0.42, y + 1.14, cw - 0.84, 0.7)
        para(tf, True, v, 13.5, False, INK, line=1.45)
    return s


def s03_numbers(prs):
    s = blank(prs)
    head(s, '국내 로봇산업은 3.2% 성장했다',
         '해외 전망치는 시장 정의에 따라 최대 9배까지 차이가 난다')

    data = [
        ('₩6.17조', KO, '2024년 국내 로봇산업 매출', '전년 대비 +3.2%'),
        ('47.9%', EN, 'SK 피지컬AI 시장 연평균 성장률', 'MarketsandMarkets, 2026→2031'),
        ('9배', KO, '한국 휴머노이드 시장 추정치 격차', '2026년, MnM vs GVR'),
    ]
    cw = (W - 0.6) / 3
    ch = 3.5
    y = band_top(ch)
    for i, (num, font, cap, sub) in enumerate(data):
        x = M + i * (cw + 0.3)
        card(s, x, y, cw, ch, TINT if i == 1 else WHITE)
        _, tf = box(s, x + 0.34, y + 0.58, cw - 0.5, 1.3, MSO_ANCHOR.MIDDLE)
        para(tf, True, num, 46, True, ROYAL if i == 1 else INK, font=font,
             line=1.0, spc=-50)
        rule(s, x + 0.34, y + 2.10, 1.3, BLUE, 2.5)
        _, tf = box(s, x + 0.34, y + 2.42, cw - 0.62, 1.0)
        para(tf, True, cap, 14, True, INK, line=1.4)
        para(tf, False, sub, 12, False, GRAY, line=1.4, before=7)

    source(s, 'Source: KIRIA 로봇산업실태조사(2025-12-29); MarketsandMarkets, '
              'Grand View Research(2026)')
    return s


def s04_table(prs):
    s = blank(prs)
    head(s, '5대 경쟁사가 전 영역을 장악하고 있다',
         '하드웨어 대기업부터 소프트웨어 플랫폼까지')

    rows = [
        ('기업', '핵심 포지셔닝', '가격·비즈니스 모델'),
        ('현대차\n(보스턴다이내믹스)', '휴머노이드 생산 선도, 2028년 연 3만대 양산 목표',
         '사내 우선 배치, 가격 비공개'),
        ('삼성전자\n(+레인보우로보틱스)', '반도체·자본 기반 패스트팔로워, 제조에서 B2B, B2C로 확장',
         '볼리 렌탈·구독 모델'),
        ('LG전자\n(+베어로보틱스)', '국내 상업용 서비스로봇 1위(Servi)', '구독형 RaaS 요금제'),
        ('두산로보틱스', '국내 협동로봇(코봇) 1위, 수출 중심', 'B2B 견적 기반, 일부 RaaS'),
        ('레인보우로보틱스', '국내 유일 휴머노이드 전문기업(삼성 계열)',
         '상용화 2027~2030년 목표'),
    ]
    hh, rh = 0.62, 0.76
    total = hh + rh * 5
    gf = s.shapes.add_table(len(rows), 3, Inches(M), Inches(band_top(total)),
                            Inches(W), Inches(total))
    t = gf.table
    t.first_row = False
    t.horz_banding = False
    for i, w in enumerate((3.15, 5.06, 3.40)):
        t.columns[i].width = Inches(w)
    t.rows[0].height = Inches(hh)
    for r in range(1, len(rows)):
        t.rows[r].height = Inches(rh)

    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            cell = t.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.2)
            cell.margin_top = cell.margin_bottom = Inches(0.1)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = (NAVY if r == 0 else
                                        (TINT if r % 2 == 0 else WHITE))
            tf = cell.text_frame
            tf.word_wrap = True
            for j, ln in enumerate(v.split('\n')):
                para(tf, j == 0, ln,
                     13 if r == 0 else (13 if c == 0 else 12.5),
                     r == 0 or c == 0,
                     WHITE if r == 0 else INK, line=1.28)
            cell_border(cell, ('B',), HAIR if r else NAVY)
    return s


def cards_row(prs, title, lead, blocks, ch=None):
    s = blank(prs)
    head(s, title, lead)
    n = len(blocks)
    gap = 0.4 if n == 3 else 0.5
    cw = (W - gap * (n - 1)) / n
    size = 13 if n == 3 else 14
    if ch is None:
        ch = 3.02 if n == 2 else 3.48
        if any(len(b) > 3 and b[3] for b in blocks):
            ch += 0.26
    y = band_top(ch)
    for i, b in enumerate(blocks):
        name, items = b[0], b[1]
        accent = b[2] if len(b) > 2 else BLUE
        sub = b[3] if len(b) > 3 else None
        topic_card(s, M + i * (cw + gap), y, cw, ch, name, items, accent, sub,
                   size)
    return s


def s07_timeline(prs):
    s = blank(prs)
    head(s, '정부는 12개월간 정책을 촘촘히 쌓았다',
         'K-휴머노이드 연합부터 AI기본법까지')

    pts = [
        ('2025.04', 'K-휴머노이드 연합 출범', '민관 1조원+ 투자 예고'),
        ('2026.01', 'AI기본법 시행', '세계 최초 포괄적 AI법률'),
        ('2026.03', 'AI로봇 M.AX 얼라이언스', '라운드테이블'),
        ('2026.05', '로봇산업기술개발사업 공고', '예산 구체화'),
    ]
    line_y = 3.42
    rule(s, M + 0.3, line_y, W - 0.6, HAIR, 1.5)
    cw = (W - 0.6) / 4
    for i, (date, t1, t2) in enumerate(pts):
        cx = M + 0.34 + i * (cw + 0.2)
        _, tf = box(s, cx - 0.06, line_y - 0.86, cw, 0.44)
        para(tf, True, date, 17, True, ROYAL, font=EN, spc=-30)
        d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx), Inches(line_y - 0.11),
                               Inches(0.22), Inches(0.22))
        solid(d, BLUE)
        flat(d)
        _, tf = box(s, cx - 0.06, line_y + 0.48, cw, 1.3)
        para(tf, True, t1, 14, True, INK, line=1.35)
        para(tf, False, t2, 13, False, GRAY, line=1.35, before=5)

    card(s, M, 5.62, W, 0.94, BAND, None)
    _, tf = box(s, M + 0.46, 5.62, W - 0.92, 0.94, MSO_ANCHOR.MIDDLE)
    para(tf, True, '정부 자체 조사: 규제적 애로의 67.2%가 과잉규제가 아닌 '
                   '법령·표준 부재. 현재는 규제보다 장려·지원 중심 국면',
         13.5, False, INK)
    return s


def s10_actions(prs):
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                            prs.slide_width, prs.slide_height)
    solid(bg, NAVY)
    flat(bg)
    head(s, '제안: 외부 시각과 사내 인지의 격차를 좁히는 3가지 액션',
         '지금 시작할 수 있는 순서로 적었습니다', dark=True)
    rule(s, M, 1.98, W, RGBColor(0x2C, 0x3A, 0x5E))

    acts = [
        ('01', '경쟁사 모니터링에 포함',
         '시장정보팀이 피지컬AI·로보틱스를 정기 경쟁사 인텔리전스 모니터링 범위에 포함'),
        ('02', '자체 공정 적용 검토',
         '자체 제조공정 자동화에 협동로봇·AI비전 도입 타당성 검토 및 국내 공급자 파일럿 논의'),
        ('03', '분기별 업데이트 체계',
         '본 보고서를 출발점으로 분기별 피지컬AI 동향 업데이트 체계를 수립'),
    ]
    cw = (W - 0.8) / 3
    ch = 3.0
    y = band_top(ch) + 0.1
    for i, (n, k, t) in enumerate(acts):
        c = card(s, M + i * (cw + 0.4), y, cw, ch,
                 RGBColor(0x16, 0x25, 0x4A), RGBColor(0x2C, 0x3A, 0x5E))
        x = M + i * (cw + 0.4)
        _, tf = box(s, x + 0.42, y + 0.44, cw - 0.84, 0.5)
        para(tf, True, n, 26, True, RGBColor(0x6F, 0x8B, 0xE8), font=EN, spc=-40)
        _, tf = box(s, x + 0.42, y + 1.06, cw - 0.84, 0.5)
        para(tf, True, k, 16, True, WHITE, line=1.25)
        _, tf = box(s, x + 0.42, y + 1.66, cw - 0.84, 1.2)
        para(tf, True, t, 13, False, RGBColor(0xB6, 0xC2, 0xDE), line=1.5)

    _, tf = box(s, M, 6.42, W, 0.4)
    para(tf, True, '피지컬AI는 더 이상 미래의 이야기가 아니다. 지금 추적을 시작해야 한다',
         14.5, True, RGBColor(0x9F, 0xB2, 0xE8))
    return s


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.3333)
    prs.slide_height = Inches(7.5)

    s01_cover(prs)
    s02_summary(prs)
    s03_numbers(prs)
    s04_table(prs)

    cards_row(prs, '현대차는 휴머노이드 양산을,\n삼성은 반도체·자본 시너지를 무기로 삼는다',
              None,
              [('현대차그룹 · 보스턴다이내믹스',
                ['2028년부터 Atlas 연 3만대 생산',
                 '조지아 Metaplant에서 Atlas PoC 이미 가동 중',
                 '소프트뱅크 잔여지분 인수, 나스닥 IPO 유력']),
               ('삼성전자 · 레인보우로보틱스',
                ['RX사업추진실 신설(2026.7), CEO 직속',
                 '제조용 휴머노이드에서 B2B, B2C로 확장 전략',
                 '레인보우 지분 35%, AI반도체·SmartThings 시너지'])])

    cards_row(prs, 'LG는 서비스로봇, 두산은 협동로봇 선두',
              '네이버는 하드웨어가 아닌 로봇 OS를 노린다',
              [('LG전자 · 베어로보틱스',
                ['국내 상업용 서비스로봇 1위(Servi)',
                 '베어로보틱스 지분 51% 인수, CLOi 통합',
                 '구독형 RaaS 요금제 제공']),
               ('두산로보틱스',
                ['국내 협동로봇(코봇) 1위',
                 '북미·유럽 수출 중심, ONExia 인수',
                 '2025년 매출 -29.6%, 적자 지속 중']),
               ('네이버랩스',
                ['하드웨어 아닌 소프트웨어·OS 지향',
                 'ARC+ARCBRAIN Flow 로봇 플랫폼',
                 '"로봇계의 안드로이드" 전략'])])

    s07_timeline(prs)

    cards_row(prs, 'VLA 파운데이션모델, 온디바이스 반도체, RaaS가 3대 기술 축이다',
              None,
              [('VLA 파운데이션모델',
                ['LLM에서 VLM, 시각-언어-행동(VLA) 모델로 진화',
                 '제조업 특화 대형행동모델(LBM) 구축',
                 '휴머노이드 실제 공장 라인에 배치 시작']),
               ('온디바이스 AI 반도체',
                ['한국 반도체 강점을 차별화 요소로',
                 '삼성·SK하이닉스 AI최적화 칩',
                 '국내화된 온디바이스 AI 칩이 해자']),
               ('RaaS · 플랫폼 비즈니스',
                ['LG·베어 Servi 구독형(RaaS)',
                 '삼성 볼리 렌탈·구독 모델',
                 '네이버 ARC 로봇 OS 플랫폼 전략'])])

    cards_row(prs, '외부는 활발히 움직이지만, 사내에는 관련 문서가 하나도 없다',
              None,
              [('외부 시각',
                ['삼성·LG·현대차 CEO 직속 조직 일제히 신설',
                 '수천억~조원 단위 자본 투입',
                 '정부는 K-휴머노이드 연합으로 국가 전략화'],
                BLUE, '가속화되는 전략적 움직임'),
               ('사내 인식',
                ['SharePoint 전수조사: 관련 시장분석·영업자료 0건',
                 'R&D 투자는 섬유·웨어러블에 전액 집중',
                 '경쟁사·공급망 자동화 전환 인지 지연 위험'],
                WARN, '공식 전략 레이더에 부재')])

    s10_actions(prs)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, NAME)
    prs.save(p)
    print(NAME, len(prs.slides._sldIdLst), '장')
    return p


if __name__ == '__main__':
    main()
