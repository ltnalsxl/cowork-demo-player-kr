// jsdom으로 실제 렌더링을 확인한다. 브라우저가 무거울 때 쓰는 대체 검증이다.
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const runsSrc = fs.readFileSync(path.join(root, 'data', 'runs.js'), 'utf8');
const fxSrc = fs.existsSync(path.join(root, 'data', 'fx.js'))
  ? fs.readFileSync(path.join(root, 'data', 'fx.js'), 'utf8') : 'window.COWORK_FX=null;';
const appSrc = fs.readFileSync(path.join(root, 'assets', 'app.js'), 'utf8');
const autosSrc = fs.existsSync(path.join(root, 'data', 'autos.js'))
  ? fs.readFileSync(path.join(root, 'data', 'autos.js'), 'utf8')
  : 'window.COWORK_AUTOS={items:[]};';

const out = [];
const ok = (label, cond, extra) =>
  out.push((cond ? '  OK   ' : '  FAIL ') + label + (extra ? '  → ' + extra : ''));

function boot(hash) {
  const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'https://x/' + (hash || '') });
  dom.window.eval(fxSrc);
  dom.window.eval(runsSrc);
  dom.window.eval(autosSrc);
  dom.window.eval(appSrc);
  return dom.window;
}

/* 묶인 회차는 홈에 대표 하나만 있으므로 탭을 거쳐 연다.
   실행·크레딧·자동화 어느 화면에서 불러도 홈으로 먼저 돌아간다. */
function openRun(w, id) {
  const tab = w.document.querySelector('.gt[data-go="' + id + '"]');
  if (tab) {
    tab.dispatchEvent(new w.Event('click', { bubbles: true }));
    return;
  }
  /* 홈 단추는 실행·크레딧 화면에만 있다. 자동화 화면에서는 사이드바를 쓴다. */
  const home = w.document.getElementById('goHome')
    || w.document.getElementById('btNew');
  if (home) { home.dispatchEvent(new w.Event('click', { bubbles: true })); }

  const btn = w.document.querySelector('.ritem[data-id="' + id + '"]');
  if (btn) {
    btn.dispatchEvent(new w.Event('click', { bubbles: true }));
    return;
  }
  /* 대표를 먼저 연 뒤 탭으로 옮긴다. */
  const g = RUNS.find((x) => x.id === id).group;
  const lead = RUNS.find((x) => x.group === g && x.groupLabel);
  w.document.querySelector('.ritem[data-id="' + lead.id + '"]')
    .dispatchEvent(new w.Event('click', { bubbles: true }));
  w.document.querySelector('.gt[data-go="' + id + '"]')
    .dispatchEvent(new w.Event('click', { bubbles: true }));
}

const RUNS = JSON.parse(runsSrc.slice(runsSrc.indexOf('[')).replace(/;\s*$/, ''));

// ── 1) 홈 화면 ──────────────────────────────────────────
{
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  const $$ = (s) => [...w.document.querySelectorAll(s)];

  ok('홈 히어로', $('.hero-q')?.textContent === '지금 무엇을 작업하고 있나요?');
  ok('재생 항목 8개', $$('.ritem').length === 8, $$('.ritem').length);
  /* 눌러도 열리지 않는 항목을 두지 않는다. 위쪽 내비게이션(새 작업, 내 작업,
     자동화, 사용자 지정)은 실제 화면 구조라 그대로 두고, 채팅 기록은 실제 회차만 세운다. */
  ok('홈에 죽은 타일 없음', $$('.tile').length === 0, $$('.tile').length);
  ok('재생 항목은 모두 열림',
    $$('.resume .ritem').every((b) => b.dataset.id), $$('.resume .ritem').length);
  ok('채팅 기록은 실제 회차만',
    $$('#chats button').length === $$('#chats button[data-id]').length,
    $$('#chats button').length + ' / ' + $$('#chats button[data-id]').length);
  ok('사이드바 내비게이션 넷', $$('#nav button').length === 4, $$('#nav button').length);
  ok('입력 힌트 줄', /팁:/.test($('.tipline')?.textContent || ''), $('.tipline')?.textContent);
  ok('컴포저 마이크', !!$('#homeCrow .micb'));
  ok('대기 중엔 보내기 없음', !$('#homeCrow .rnd'));
  ok('계정 Copilot User', /Copilot User/.test($('.me')?.textContent));
  ok('사이드바 시나리오 8개', $$('#chats button[data-id]').length === 8,
    $$('#chats button[data-id]').length);
  ok('홈 타일 제목이 회차별로 구분됨',
    new Set($$('.ritem[data-id] .rtitle').map((e) => e.textContent)).size === 8);
  /* 크레딧을 재지 않은 회차는 싣지 않는다. */
  ok('미측정 회차 없음', RUNS.every((r) => r.credit || r.variants),
    RUNS.filter((r) => !r.credit && !r.variants).map((r) => r.id).join(', '));
  /* 묶인 회차는 대표 하나만 홈에 세운다. */
  const groups = new Set(RUNS.filter((r) => r.group).map((r) => r.group));
  ok('묶음은 대표만 홈에',
    $$('.ritem[data-id]').length === RUNS.length - (RUNS.filter((r) => r.group).length - groups.size),
    $$('.ritem[data-id]').length);
  /* 모델을 바꿔 여러 번 잰 회차는 한 값이 아니라 범위로 적는다. */
  const vr = RUNS.find((r) => r.variants);
  if (vr) {
    const vals = Object.keys(vr.variants).map((k) => vr.variants[k].credit);
    const want = Math.min(...vals).toLocaleString('ko-KR') + '~' +
      Math.max(...vals).toLocaleString('ko-KR') + ' 크레딧';
    ok('여러 모델 회차는 크레딧 범위로',
      $('.ritem[data-id="' + vr.id + '"] .rcost')?.textContent === want,
      $('.ritem[data-id="' + vr.id + '"] .rcost')?.textContent);
  }
  w.close();
}

// ── 1-2) 재생 속도 ─────────────────────────────────────
{
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  w.document.querySelector('.ritem[data-id]').dispatchEvent(new w.Event('click', { bubbles: true }));
  const sp = $('#sp');
  ok('속도 단계 18개', sp.min === '0' && sp.max === '17', sp.min + '~' + sp.max);
  ok('기본 1.2배', $('#spv')?.textContent === '1.2×', $('#spv')?.textContent);
  ok('기본값이 슬라이더 위치와 맞음', sp.value === '7', sp.value);
  const set = (v) => {
    sp.value = String(v);
    sp.dispatchEvent(new w.Event('input', { bubbles: true }));
    return $('#spv').textContent;
  };
  ok('가장 느림 0.5배', set(0) === '0.5×');
  ok('1.0배 지점', set(5) === '1.0×');
  ok('0.1 간격', set(6) === '1.1×' && set(14) === '1.9×');
  ok('가장 빠름 3.0배', set(17) === '3.0×');
  /* 단계마다 화면에 붙는 양이 달라 머무는 시간도 달라야 한다.
     도구 한 줄과 최종 답변에 같은 시간을 주면 한쪽은 지루하고 한쪽은 못 읽는다. */
  ok('내용 길이에 따라 대기 시간이 다름', /dwell/.test(appSrc) && !/setInterval/.test(appSrc));
  w.close();
}

// ── 2) 시나리오별 재생 ──────────────────────────────────
const EXPECT = {
  'tc04-sonnet': { steps: 5, arts: 2, credit: '2,126' },
  'tc04-terra': { steps: 3, arts: 2, credit: '1,614' },
  'badge-check': { steps: 0, arts: 4, credit: '789' },
  'isms-audit': { steps: 4, arts: 4, credit: '1,130' },
  'daily-brief': { steps: 0, arts: 0, credit: '107' },
  'skill-proofread': { steps: 0, arts: 0, credit: '25' },
  'weekly-team': { steps: 4, arts: 1, credit: '271' },
  'rfp-deck': { steps: 0, arts: 2, credit: '348' },
  'rfp-sonnet': { steps: 0, arts: 2, credit: '253' },
  'inbox-triage': { steps: 4, arts: 1, credit: '755' }
};

RUNS.forEach((r) => {
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  const $$ = (s) => [...w.document.querySelectorAll(s)];
  const ex = EXPECT[r.id];
  const tag = r.id.padEnd(12);

  openRun(w, r.id);

  ok(tag + '상단 제목', $('.tb-title h1')?.textContent === r.chatTitle);
  if (r.promptAt) {
    ok(tag + '설치 단계 뒤에 프롬프트', !$('.ubub'));
  } else {
    ok(tag + '프롬프트 말풍선', !!$('.ubub'));
  }
  if (r.prompt.split('\n').length > 6 && !r.promptAt) {
    ok(tag + '더 보기 버튼', $('#pfold')?.textContent === '더 보기');
  } else {
    ok(tag + '짧은 프롬프트는 더 보기 없음', !$('#pfold'));
  }  ok(tag + '작업 영역 단계 ' + ex.steps, $$('#steps li').length === ex.steps,
    $$('#steps li').length);
  ok(tag + '빈 섹션은 그리지 않음',
    (/단계/.test(w.document.getElementById('panel').textContent) === ex.steps > 0) &&
    (/기술 및 플러그 인/.test(w.document.getElementById('panel').textContent) ===
      ((r.skills || []).length > 0 || !!r.skillsButton)));

  $('#skip').dispatchEvent(new w.Event('click', { bubbles: true }));

  const n = r.log.length + 1;
  ok(tag + '진행 카운터', $('#cnt')?.textContent === n + '/' + n, $('#cnt')?.textContent);
  ok(tag + '아바타 없음', $$('.abadge').length === 0);
  ok(tag + '말풍선 잔재 없음', $$('.row').length === 0);
  ok(tag + '상태 줄 제거됨', !$('#statusRow'));
  const multiFinal = r.log.filter((s) => s.t === 'final').length > 1;
  if (!multiFinal) {
    ok(tag + '산출물 카드 ' + ex.arts, $$('.fcard').length === ex.arts, $$('.fcard').length);
  }
  ok(tag + '출력 목록 ' + ex.arts, $$('#outs li').length === ex.arts);
  if (ex.arts) {
    ok(tag + '출력 항목 클릭 가능', $$('#outs .outbtn').length === ex.arts,
      $$('#outs .outbtn').length);
    /* 미리보기가 없는 산출물은 왜 없는지 그대로 적는다. 뭉뚱그리지 않는다. */
    (r.artifacts || []).forEach((a, i) => {
      if ((a.pages || []).length) { return; }
      $$('#outs .outbtn')[i].dispatchEvent(new w.Event('click', { bubbles: true }));
      const t = $('#viewer .vnone')?.textContent || '';
      const want = a.labeled ? /민감도 레이블/
        : a.kind.indexOf('메일') > -1 ? /임시보관함/ : /받아 두지 못했습니다/;
      ok(tag + '미리보기 없는 이유 ' + (i + 1), want.test(t), t.slice(0, 40));
    });
  }
  ok(tag + '비용 패널', !!$('#costrow .cost'));
  if (r.bench.shared) {
    /* 세 실행이 나눠 갖는 표는 실행 안에서 한 줄로 접고 모아보기로 넘긴다. */
    ok(tag + '벤치 접힘', !!$('.bench.slim'));
    ok(tag + '전체 비교 단추', !!$('.gotocost'));
    ok(tag + '축 표시', /축 비교에 속합니다/.test($('.bench.slim .lead')?.textContent || ''));
  } else {
    ok(tag + '벤치 행', $$('.brow').length === r.bench.models.length, $$('.brow').length);
    ok(tag + '측정 조건 표시', /측정 조건/.test($('.bcond')?.textContent || ''));
  }

  if (ex.credit) {
    ok(tag + '실측 크레딧 ' + ex.credit, $('#costrow .cost .l1 b')?.textContent === ex.credit,
      $('#costrow .cost .l1 b')?.textContent);
    ok(tag + '작업 누적 안내', /작업 전체를 셉니다/.test($('#costrow .cost .l2')?.textContent || ''));
  } else {
    ok(tag + '크레딧 미확인 안내',
      /를 찍지 않았습니다/.test($('#costrow .cost .l1')?.textContent || ''));
  }
  ok(tag + '이번 달 누계 없음', !/이번 달/.test(w.document.body.textContent));
  ok(tag + '외부 기준값 없음', !/글로벌 기준값/.test(w.document.body.textContent));

  // 로그 타입별 렌더 확인
  const types = {};
  r.log.forEach((s) => { types[s.t] = (types[s.t] || 0) + 1; });
  if (types.think) {
    ok(tag + '사고 과정 ' + types.think,
      $$('.think:not(.inner)').length === types.think, $$('.think:not(.inner)').length);
  }
  if (types.edit) {
    ok(tag + '문서 편집 ' + types.edit, $$('.edits').length === types.edit, $$('.edits').length);
    const failed = r.log.filter((s) => s.t === 'edit' && s.failed).length;
    ok(tag + '편집 실패 배지 ' + failed, $$('.badge-x').length === failed, $$('.badge-x').length);
  }
  if (types.search) {
    ok(tag + '웹 검색 블록', $$('.websearch').length === types.search);
    const urls = r.log.filter((s) => s.t === 'search')
      .reduce((a, s) => a + s.queries.reduce((b, q) => b + q.urls.length, 0), 0);
    ok(tag + 'URL 링크 ' + urls, $$('.wq .urls a').length === urls, $$('.wq .urls a').length);
  }
  if (types.tools) {
    ok(tag + '도구 묶음 ' + types.tools, $$('.tgroup').length === types.tools, $$('.tgroup').length);
  }
  if (types.tool) {
    ok(tag + '단일 도구 줄', $$('.tool').length >= types.tool);
  }
  if (types.find) {
    ok(tag + '파일 검색 ' + types.find, $$('.find').length === types.find);
  }
  if (types.agent) {
    ok(tag + '서브 에이전트 ' + types.agent, $$('.agent').length === types.agent);
  }
  if (types.ask) {
    ok(tag + '되묻기 블록 ' + types.ask, $$('.askwrap').length === types.ask);
    const qs = r.log.filter((s) => s.t === 'ask').reduce((a, s) => a + s.items.length, 0);
    ok(tag + '질문 ' + qs + '개', $$('.askq').length === qs, $$('.askq').length);
    ok(tag + '고른 답만 강조', $$('.askq .opt.on').length === qs, $$('.askq .opt.on').length);
  }

  if (types.mail) {
    ok(tag + '메일 승인 카드', $$('.mailcard:not(.confirm)').length === types.mail);
    ok(tag + '보내기 버튼', $$('.mailcard:not(.confirm) .mb.send').length === types.mail);
    const withTo = r.log.filter((s) => s.t === 'mail' && s.to).length;
    ok(tag + '받는 사람 pill ' + withTo, $$('.mailcard .pill-p').length === withTo,
      $$('.mailcard .pill-p').length);
    const noSend = r.log.filter((s) => s.t === 'mail' && s.disabled).length;
    if (noSend) {
      ok(tag + '수신자 없으면 보내기 비활성', $$('.mailcard.nosend').length === noSend);
    }
    /* 메일 카드는 첨부 버튼까지 5개, Teams 채팅 카드는 첨부가 없어 4개다. */
    const chatN = r.log.filter((s) => s.t === 'mail' && s.chat).length;
    ok(tag + '서식 툴바', $$('.mailcard .mtb button').length >= types.mail * 4 + (types.mail - chatN));
    if (chatN) {
      ok(tag + 'Teams 채팅 카드 ' + chatN, $$('.mailcard.chat').length === chatN);
      ok(tag + '채팅엔 제목 없음', !$$('.mailcard.chat .msub').length);
      ok(tag + '채팅 승인 버튼',
        /Post message 항상 허용/.test($('.mailcard.chat .mb.send')?.textContent || ''));
    }
    const att = r.log.filter((s) => s.t === 'mail')
      .reduce((a, s) => a + (s.files || []).length, 0);
    ok(tag + '메일 첨부 ' + att, $$('.matt .attc').length === att, $$('.matt .attc').length);
    const tbl = r.log.filter((s) => s.t === 'mail' && /\n\| /.test(s.body)).length;
    if (tbl) { ok(tag + '메일 본문 표', $$('.mailcard .mbody table').length >= 1); }
    ok(tag + '승인 전 안내', /편집 내용이 삭제되고/.test($('.mnote')?.textContent || ''));
  }
  if (types.approved) {
    ok(tag + '승인 줄 ' + types.approved, $$('.approved').length === types.approved);
    const sent = r.log.filter((s) => s.t === 'approved' && s.sent).map((s) => s.sent);
    const shown = $$('.approved .tool').map((e) => e.textContent.trim());
    ok(tag + '승인 뒤 결과 줄', sent.every((x) => shown.includes(x)), shown.join(' / '));
  }
  if (types.schedule) {
    ok(tag + '되풀이 작업 카드 ' + types.schedule,
      $$('.mailcard.sched').length === types.schedule, $$('.mailcard.sched').length);
    ok(tag + '반복 주기 선택', $$('.mailcard.sched .selv').length >= types.schedule * 3);
    ok(tag + '지금 한 번 실행 체크', $$('.mailcard.sched .once input').length === types.schedule);
    ok(tag + '작업 설명 표시', $$('.mailcard.sched .sdesc').length === types.schedule);
  }
  if (r.scheduled) {
    const panel = w.document.getElementById('panel').textContent;
    ok(tag + '예약된 작업 섹션', /예약된 작업/.test(panel));
    ok(tag + '예약 이름', $('.schrow .sn')?.textContent === r.scheduled.name,
      $('.schrow .sn')?.textContent);
    ok(tag + '예약 주기', $('.schrow .sw')?.textContent === r.scheduled.when);
  } else {
    ok(tag + '예약 없으면 섹션 없음',
      !/예약된 작업/.test(w.document.getElementById('panel').textContent));
  }
  if (r.variants) {
    const names = Object.keys(r.variants);
    ok(tag + '모델별 결과 ' + names.length, $$('.varybox').length >= 1);
    ok(tag + '기본 모델 표시', $('.vmdl')?.textContent === r.model, $('.vmdl')?.textContent);
    ok(tag + '벤치 행이 모델 수와 같음', $$('.brow').length === names.length);
    const body0 = $('.varybox .asay').textContent;
    /* 모델을 바꾸면 답변과 크레딧이 함께 바뀐다. */
    const other = names.filter((n) => n !== r.model)[0];
    $$('#crow .pop-wrap')[1].querySelector('.pill')
      .dispatchEvent(new w.Event('click', { bubbles: true }));
    $$('#crow .pop.on .mi').find((m) => m.textContent.indexOf(other) === 0)
      .dispatchEvent(new w.Event('click', { bubbles: true }));
    ok(tag + '모델 바꾸면 답변 교체', $('.varybox .asay').textContent !== body0);
    ok(tag + '바뀐 모델 이름', $('.vmdl')?.textContent === other, $('.vmdl')?.textContent);
    ok(tag + '바뀐 모델 크레딧',
      $('#costrow .cost .l1 b')?.textContent === String(r.variants[other].credit),
      $('#costrow .cost .l1 b')?.textContent);
    ok(tag + '바뀐 모델 기본 노력',
      $('#effLabel')?.textContent === r.variants[other].effort, $('#effLabel')?.textContent);
    /* 측정하지 않은 모델은 답을 만들지 않는다. */
    $$('#crow .pop-wrap')[1].querySelector('.pill')
      .dispatchEvent(new w.Event('click', { bubbles: true }));
    $$('#crow .pop.on .mi').find((m) => m.textContent.indexOf('자동') === 0)
      .dispatchEvent(new w.Event('click', { bubbles: true }));
    ok(tag + '미측정 모델은 답변 비움', !!$('.vnone2'));
  }
  if (types.stage) {
    ok(tag + '설치 화면 ' + types.stage, $$('.stage').length === types.stage, $$('.stage').length);
    ok(tag + '설치 화면마다 설명', $$('.stage .sgcap').length === types.stage);
    const hl = r.log.filter((s) => s.t === 'stage').filter((s) => {
      const sc = s.screen || {};
      return sc.hl || sc.menuHl !== undefined || (sc.secs || []).some((g) =>
        (g.rows || []).some((x) => x.hl)) || (sc.tabs || []).some((t) => t.hl);
    }).length;
    ok(tag + '누른 자리 표시 ' + hl, $$('.stage .hl').length >= hl, $$('.stage .hl').length);
    ok(tag + '설치 뒤 프롬프트 나옴', !!$('.ubub'));
    const stages = $$('.stage');
    const bubbles = $$('.uwrap');
    ok(tag + '프롬프트가 설치 뒤에 옴',
      stages[stages.length - 1].compareDocumentPosition(bubbles[0]) === 4);
  }
  if (r.allowed) {
    ok(tag + '항상 허용됨 ' + r.allowed.length,
      $$('.allow li').length === r.allowed.length, $$('.allow li').length);
    ok(tag + '항상 허용 섹션 제목',
      /항상 허용됨/.test(w.document.getElementById('panel').textContent));
  } else {
    ok(tag + '허용 목록 없으면 섹션 없음',
      !/항상 허용됨/.test(w.document.getElementById('panel').textContent));
  }
  if (types.confirm) {
    ok(tag + '도구 승인 카드', $$('.mailcard.confirm:not(.sched)').length === types.confirm);
    const rows = r.log.filter((s) => s.t === 'confirm')
      .reduce((a, s) => a + s.rows.length, 0);
    ok(tag + '승인 카드 값 ' + rows, $$('.krow').length === rows, $$('.krow').length);
    /* 안내 문구는 회차마다 다를 수 있다. note를 준 회차는 그 문구가, 없으면 기본 문구가 뜬다. */
    const want = r.log.filter((s) => s.t === 'confirm')
      .map((s) => s.note || '승인하기 전에 세부 정보를 검토하세요.');
    const shown = $$('.mailcard.confirm .cnote').map((e) => e.textContent.trim());
    ok(tag + '검토 안내', want.every((x) => shown.includes(x)), shown.join(' / '));
  }
  if (r.log.filter((s) => s.t === 'final').length > 1) {
    /* 턴마다 그 턴의 산출물만 붙는다. 전체 합이 artifacts 수와 같아야 한다. */
    const shown = r.log.filter((s) => s.t === 'final')
      .reduce((a, s) => a + (s.out ? s.out.length : r.artifacts.length), 0);
    ok(tag + '턴별 산출물 카드 ' + shown, $$('.fcard').length === shown, $$('.fcard').length);
    ok(tag + '출력 목록은 전체 ' + ex.arts, $$('#outs li').length === ex.arts);
  }
  if (types.cost) {
    /* 대화 도중에 찍은 /cost는 마지막 비용 패널과 별개로 남는다. */
    ok(tag + '중간 /cost ' + types.cost, $$('.cost').length === types.cost + 1,
      $$('.cost').length);
    const last = r.log.filter((s) => s.t === 'cost').pop();
    ok(tag + '중간 /cost 값', [...$$('.cost .l1 b')].map((e) => e.textContent)
      .includes(last.credit.toLocaleString('en-US')));
  }
  if (types.prompt) {
    ok(tag + '이어 시킨 프롬프트 ' + types.prompt,
      $$('.umeta .num').length === types.prompt + 1, $$('.umeta .num').length);
    ok(tag + '턴 구분선', $$('.daysep').length === types.prompt + 1, $$('.daysep').length);
    const longP = r.log.filter((s) => s.t === 'prompt' && s.body.split('\n').length > 6).length +
      (r.prompt.split('\n').length > 6 ? 1 : 0);
    ok(tag + '긴 프롬프트 접힘 ' + longP, $$('.fold').length === longP, $$('.fold').length);
  }
  if (r.skillsButton) {
    ok(tag + '기술 관리 버튼', !!w.document.querySelector('.tag.mng'));
  }
  // 도구 묶음 안에 낀 사고 과정
  const inner = r.log.filter((s) => s.t === 'tools')
    .reduce((a, s) => a + (s.items || []).filter((x) => x.think).length, 0);
  if (inner) {
    ok(tag + '묶음 안 사고 과정 ' + inner, $$('.tgroup .think.inner').length === inner,
      $$('.tgroup .think.inner').length);
  }

  // 첨부와 참조
  if ((r.promptFiles || []).length) {
    ok(tag + '프롬프트 첨부 ' + r.promptFiles.length,
      $$('.uatt .chipf').length === r.promptFiles.length, $$('.uatt .chipf').length);
  }
  if ((r.refs || []).length) {
    ok(tag + '참조 섹션', /참조/.test(w.document.getElementById('panel').textContent));
  }
  ok(tag + '도구 섹션 표시', /도구/.test(w.document.getElementById('panel').textContent) ===
    ((r.tools || []).length > 0));

  // 단계 상태
  const labels = $$('.steps li .ss').map((e) => e.textContent);
  if (!ex.steps) {
    ok(tag + '단계 없음', labels.length === 0 && !w.document.getElementById('stepn'));
  } else if (r.stepStates) {
    ok(tag + '단계 상태 실행 기록대로', labels.join('/') === r.stepStates.join('/'), labels.join('/'));
    const doneN = r.stepStates.filter((x) => x === '완료됨').length;
    ok(tag + '단계 카운터', $('#stepn')?.textContent === doneN + '/' + ex.steps,
      $('#stepn')?.textContent);
  } else {
    ok(tag + '단계 모두 완료됨', labels.every((x) => x === '완료됨'));
  }

  w.close();
});

// ── 3) 모델 전환 (TC-04) ────────────────────────────────
{
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  const $$ = (s) => [...w.document.querySelectorAll(s)];

  openRun(w, 'tc04-sonnet');
  $('#skip').dispatchEvent(new w.Event('click', { bubbles: true }));

  ok('전환 전 실측 2,126', $('.cost .l1 b')?.textContent === '2,126', $('.cost .l1 b')?.textContent);

  const mdlBtn = $$('#crow .pop-wrap')[1].querySelector('.pill');
  mdlBtn.dispatchEvent(new w.Event('click', { bubbles: true }));
  const terra = $$('#crow .pop.on .mi').find((m) => /Terra/.test(m.textContent));
  terra.dispatchEvent(new w.Event('click', { bubbles: true }));

  ok('모델 전환 반영', $('.cost .l1 b')?.textContent === '1,614', $('.cost .l1 b')?.textContent);
  ok('막대 강조 이동', /Terra/.test($('.bnm.self')?.textContent || ''));
  ok('라벨 갱신', /Terra/.test($('#mdlLabel')?.textContent || ''));
  ok('노력 기본값 자동 변경', $('#effLabel')?.textContent === '매우 높음', $('#effLabel')?.textContent);
  w.close();
}

// ── 3-2) 측정하지 않은 조합은 값을 만들지 않는다 ────────
{
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  const $$ = (s) => [...w.document.querySelectorAll(s)];

  openRun(w, 'isms-audit');
  $('#skip').dispatchEvent(new w.Event('click', { bubbles: true }));
  ok('전환 전 실측 1,130', $('.cost .l1 b')?.textContent === '1,130', $('.cost .l1 b')?.textContent);

  $$('#crow .pop-wrap')[1].querySelector('.pill')
    .dispatchEvent(new w.Event('click', { bubbles: true }));
  $$('#crow .pop.on .mi').find((m) => /Terra/.test(m.textContent))
    .dispatchEvent(new w.Event('click', { bubbles: true }));

  ok('미측정 조합 안내', /측정하지 않았습니다/.test($('.cost .l1')?.textContent || ''),
    $('.cost .l1')?.textContent);
  ok('미측정 조합 숫자 없음', !$('.cost .l1 b')?.textContent.match(/^[\d,]+$/));
  w.close();
}

// ── 4) 개인정보 ────────────────────────────────────────
{
  const w = boot();
  const bad = /이수민|Sumin|suminlee|사내 한정|Cloud Solution|롯데|삼성|SK ?플래닛|SK디스커버리|11번가|GO\+|VBD|ROSS|PQMT|NVIDIA|diax|onmicrosoft|MOD Administrator|포스코|카리플렉스|대림|FastTrack|Sang-In|Jinsup|Hyun Ko|Karen Kong|Elaine|박민욱|김지민|박정수|최정우|AX교육팀/;
  RUNS.forEach((r) => {
    openRun(w, r.id);
    w.document.getElementById('skip').dispatchEvent(new w.Event('click', { bubbles: true }));
    const hits = w.document.body.textContent.split('\n').filter((l) => bad.test(l));
    ok('식별 정보 없음 ' + r.id, hits.length === 0, hits.slice(0, 2).join(' / '));
  });
  w.close();
}

/* 4-2) 익명화하며 만든 대체어가 도로 새어 들어오지 않는지 본다.
   "고객사 A"류는 지웠다는 표시가 남은 것이라 그 자체가 티가 난다. */
{
  const w = boot();
  const leak = /고객사 [A-H]|고객 [A-H]\b|도입 프로그램|내부 교육 과정|고객 워크숍|업무 배정 시스템|품질 측정|파트너사|지원 프로그램|요청번호 R-0000/;
  RUNS.forEach((r) => {
    openRun(w, r.id);
    w.document.getElementById('skip').dispatchEvent(new w.Event('click', { bubbles: true }));
    const hits = w.document.body.textContent.split('\n').filter((l) => leak.test(l));
    ok('대체어 잔재 없음 ' + r.id, hits.length === 0, hits.slice(0, 2).join(' / '));
  });
  w.close();
}

/* 4-3) 회차 묶음 — 계정이나 모델이 다른 실행을 한 창에서 오간다. */
{
  const w = boot();
  const $$ = (s) => [...w.document.querySelectorAll(s)];
  const groups = {};
  RUNS.forEach((r) => { if (r.group) { (groups[r.group] = groups[r.group] || []).push(r); } });
  Object.keys(groups).forEach((g) => {
    const set = groups[g];
    const lead = set.find((r) => r.groupLabel);
    ok('묶음 대표 하나 ' + g, set.filter((r) => r.groupLabel).length === 1);
    openRun(w, lead.id);
    ok('탭 ' + g + ' ' + set.length + '개', $$('.gt').length === set.length, $$('.gt').length);
    ok('현재 탭 표시 ' + g, $$('.gt.on').length === 1);
    /* 다른 탭을 누르면 그 회차로 갈아탄다. */
    const other = set.find((r) => r.id !== lead.id);
    w.document.querySelector('.gt[data-go="' + other.id + '"]')
      .dispatchEvent(new w.Event('click', { bubbles: true }));
    ok('탭 전환 ' + g,
      w.document.querySelector('.tb-title h1').textContent === other.chatTitle,
      w.document.querySelector('.tb-title h1').textContent);
    ok('탭마다 크레딧 표시 ' + g,
      $$('.gt .gc').length === set.length, $$('.gt .gc').length);
  });
  w.close();
}

/* 4-4) 크레딧 옆 원화 — 환율을 받아 둔 날만 붙는다. */
{
  const w = boot();
  const fx = w.COWORK_FX;
  openRun(w, 'isms-audit');
  w.document.getElementById('skip').dispatchEvent(new w.Event('click', { bubbles: true }));
  const t = w.document.querySelector('#costrow .cost .l1')?.textContent || '';
  if (fx) {
    const want = Math.round(1130 / 100 * fx.usdkrw).toLocaleString('ko-KR');
    ok('원화 병기', t.indexOf('약 ' + want + '원') > -1, t);
  } else {
    ok('환율 없으면 달러만', !/원/.test(t), t);
  }
  ok('작업 수준 라벨', /작업 수준/.test(w.document.querySelector('.tb-title .sub')?.textContent || ''));
  if (fx) {
    /* isms-audit은 표를 접으므로 환율 출처는 모아보기에서 확인한다. */
    w.location.hash = 'credits';
    w.dispatchEvent(new w.Event('hashchange'));
    ok('환율 출처 표기', /환율/.test(w.document.querySelector('.cx-foot')?.textContent || ''));
  }
  w.close();
}

/* 4-5) 크레딧 모아보기 — 축이 셋이고, 나눠 갖는 표는 한 번만 선다. */
{
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  const $$ = (s) => [...w.document.querySelectorAll(s)];
  w.location.hash = 'credits';
  w.dispatchEvent(new w.Event('hashchange'));

  ok('모아보기 축 3개', $$('.cx-ax').length === 3, $$('.cx-ax').length);
  ok('모아보기 축 이름',
    $$('.cx-tag').map((e) => e.textContent).join(',') === '모델만 바꿈,계정만 바꿈,작업만 바꿈',
    $$('.cx-tag').map((e) => e.textContent).join(','));

  /* 같은 표를 나눠 갖는 회차는 표를 한 번만 세우고 실행 단추를 여럿 낸다. */
  const runs = w.COWORK_RUNS;
  const shared = runs.filter((r) => r.bench && r.bench.shared);
  ok('나눠 갖는 표 하나로', $$('.cx-g').length === 6, $$('.cx-g').length);
  const last = $$('.cx-g').slice(-1)[0];
  ok('나눠 갖는 실행 모두 표시',
    last.querySelectorAll('.cx-go').length === shared.length,
    last.querySelectorAll('.cx-go').length);
  ok('실행별 꼬리 제거',
    !/271은|789는|1,130은/.test(last.querySelector('.bcond')?.textContent || ''));

  /* 모든 회차의 표가 빠짐없이 실려야 한다. */
  const want = new Set(runs.filter((r) => r.bench && r.bench.models)
    .map((r) => r.bench.axis + '|' + (r.bench.head || '')));
  ok('표 개수가 축·머리글 조합과 같음', $$('.cx-g').length === want.size, want.size);

  ok('모아보기 → 실행 이동', !!$('.cx-go'));
  $('.cx-go').dispatchEvent(new w.Event('click', { bubbles: true }));
  ok('실행으로 넘어감', !!$('#costrow') || !!$('.ctrl'));
  w.close();
}

/* 4-6) 자동화 — 목록과 상세, 대화에서 건너가기. */
{
  const w = boot();
  const $ = (s) => w.document.querySelector(s);
  const $$ = (s) => [...w.document.querySelectorAll(s)];
  const autos = w.COWORK_AUTOS.items;

  /* 사이드바에서 연다. 실제 화면과 같은 진입점이다. */
  w.document.getElementById('btAutos')
    .dispatchEvent(new w.Event('click', { bubbles: true }));
  ok('자동화 목록', $$('.au-card').length === autos.length, $$('.au-card').length);
  ok('자동화 사이드바 표시', $('#btAutos')?.classList.contains('on'));
  ok('자동화 주소', w.location.hash === '#autos', w.location.hash);

  autos.forEach((a) => {
    const card = $$('.au-card').filter((c) => c.dataset.a === a.id)[0];
    ok('자동화 카드 ' + a.id, !!card);
    const cy = card?.querySelector('.au-cy')?.textContent || '';
    ok('자동화 주기 ' + a.id,
      a.paused ? /일시 중지/.test(cy) : cy.indexOf(a.every) > -1, cy.slice(0, 44));
  });

  /* 상세 — 예약, 지시문, 알림 위치, 실행 기록이 모두 서야 한다. */
  autos.forEach((a) => {
    w.location.hash = 'autos/' + a.id;
    w.dispatchEvent(new w.Event('hashchange'));
    const tag = '자동화 상세 ' + a.id + ' ';
    ok(tag + '제목', $('.au-dh h1')?.textContent === a.name, $('.au-dh h1')?.textContent);
    ok(tag + '상태', $('.au-badge')?.textContent === a.state);
    ok(tag + '토글', $('.au-tg')?.classList.contains('on') === !a.paused);
    ok(tag + '다음 실행', !!$('.au-next') === !!a.next);
    ok(tag + '지시문', ($('.au-body')?.textContent || '') === a.desc);
    ok(tag + '알림 위치',
      $('.au-r.on b')?.textContent === a.where, $('.au-r.on b')?.textContent);
    ok(tag + '실행 기록', $$('.au-run-row').length === a.runs.length);
    /* 실행 결과는 끝난 것, 실패한 것, 도는 것으로 갈린다. */
    const states = $$('.au-run-row .w').map((e) => e.className.replace('w ', ''));
    ok(tag + '실행 상태',
      states.join(',') === a.runs.map((x) => x.state || 'ok').join(','), states.join(','));
    /* 대화가 남지 않은 실행은 그렇다고 적는다. */
    ok(tag + '대화 없음 표시',
      $$('.au-run-row .nc').length === a.runs.filter((x) => x.noChat).length);
    /* 산출물이 남은 실행에는 파일 칩이 붙는다. */
    ok(tag + '실행 산출물',
      $$('.au-run-row .f').length === a.runs.filter((x) => x.file).length);
    /* 만들어 둔 대화가 있는 자동화만 건너가기 단추가 붙는다. */
    ok(tag + '작업으로 이동', !!$('.au-go') === !!a.run);
  });

  /* 개인정보가 남지 않아야 한다. */
  const raw = JSON.stringify(autos);
  ok('자동화 실명 없음', !/Sumin|수민/i.test(raw));
  ok('자동화 메일 주소 없음', !/[\w.]+@[\w.]+/.test(raw));
  ok('자동화 고객사명 없음', !/Samsung|삼성|현대|LG전자/i.test(raw));
  ok('자동화 테넌트 주소 없음', !/planner\.cloud|sharepoint\.com|72f988bf/i.test(raw));

  /* 대화에서도 자동화로 건너갈 수 있다. */
  openRun(w, 'daily-brief');
  w.document.getElementById('skip').dispatchEvent(new w.Event('click', { bubbles: true }));
  const jump = $('.au-jump');
  ok('대화에서 자동화 링크', !!jump);
  if (jump) {
    jump.dispatchEvent(new w.Event('click', { bubbles: true }));
    ok('링크로 자동화 열림', $('.au-dh h1')?.textContent === '평일 아침 브리핑 (Teams)',
      $('.au-dh h1')?.textContent);
  }
  w.close();
}

/* 4-7) 파비콘 — 없으면 브라우저가 임의의 글자 아이콘을 만든다. */
{
  const w = boot();
  const links = [...w.document.querySelectorAll('link[rel*="icon"]')];
  ok('파비콘 선언', links.length >= 2, links.length);
  links.forEach((l) => {
    const p = l.getAttribute('href');
    ok('파비콘 파일 ' + p, fs.existsSync(path.join(root, p)));
  });
  w.close();
}

console.log(out.join('\n'));
const fails = out.filter((l) => l.startsWith('  FAIL')).length;
console.log('\n' + (out.length - fails) + '/' + out.length + ' 통과');
process.exit(fails ? 1 : 0);


