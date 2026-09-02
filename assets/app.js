/* Cowork 데모 플레이어 — 실행 로그 재생 + /cost 실측 비교 */
(function () {
  'use strict';

  var RUNS = window.COWORK_RUNS || [];
  var app = document.getElementById('app');
  var stream = null;
  var run = null, idx = 0, timer = null, speed = 2, costShown = false,
      picked = null, effortPick = null, running = false;

  var fmt = function (n) { return Number(n).toLocaleString('ko-KR'); };
  var usd = function (c) { return '$' + (c / 100).toFixed(2); };

  /* ── 아이콘 (Fluent 계열 선 아이콘) ── */
  var I = {
    grid: '<svg width="17" height="17" viewBox="0 0 20 20" fill="currentColor"><circle cx="4" cy="4" r="1.4"/><circle cx="10" cy="4" r="1.4"/><circle cx="16" cy="4" r="1.4"/><circle cx="4" cy="10" r="1.4"/><circle cx="10" cy="10" r="1.4"/><circle cx="16" cy="10" r="1.4"/><circle cx="4" cy="16" r="1.4"/><circle cx="10" cy="16" r="1.4"/><circle cx="16" cy="16" r="1.4"/></svg>',
    check: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="3" y="3" width="14" height="14" rx="3"/><path d="M6.6 10.2l2.2 2.2 4.5-4.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    panel: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="2.5" y="3.5" width="15" height="13" rx="2.5"/><path d="M12 3.5v13"/></svg>',
    plusC: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><circle cx="10" cy="10" r="9"/><path d="M10 6v8M6 10h8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/></svg>',
    tasks: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><path d="M2.5 5l1.6 1.6L7 3.7M2.5 11l1.6 1.6L7 9.7M2.5 17l1.6 1.6L7 15.7M9.5 5h8M9.5 11h8M9.5 17h8"/></svg>',
    bolt: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M11.2 2L4.5 11h4.3l-.9 7 6.8-9h-4.3z"/></svg>',
    brain: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M7.7 3.1a2.1 2.1 0 00-2.1 2 2 2 0 00-1.4 3.2 2.1 2.1 0 00.5 3.3 2.1 2.1 0 003 2.2"/><path d="M12.3 3.1a2.1 2.1 0 012.1 2 2 2 0 011.4 3.2 2.1 2.1 0 01-.5 3.3 2.1 2.1 0 01-3 2.2"/><path d="M10 3.6v12.8M7.7 3.1A2.3 2.3 0 0110 3.6a2.3 2.3 0 012.3-.5M7.7 13.8a2.3 2.3 0 002.3 2.6 2.3 2.3 0 002.3-2.6"/></svg>',
    gear: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><circle cx="10" cy="10" r="2.5"/><path d="M16.1 11.9a1.1 1.1 0 00.2 1.2l.1.1a1.3 1.3 0 11-1.9 1.9l-.1-.1a1.1 1.1 0 00-1.2-.2 1.1 1.1 0 00-.7 1v.2a1.3 1.3 0 11-2.7 0v-.1a1.1 1.1 0 00-.7-1 1.1 1.1 0 00-1.2.2l-.1.1a1.3 1.3 0 11-1.9-1.9l.1-.1a1.1 1.1 0 00.2-1.2 1.1 1.1 0 00-1-.7h-.2a1.3 1.3 0 110-2.7h.1a1.1 1.1 0 001-.7 1.1 1.1 0 00-.2-1.2l-.1-.1a1.3 1.3 0 111.9-1.9l.1.1a1.1 1.1 0 001.2.2h.1a1.1 1.1 0 00.7-1v-.2a1.3 1.3 0 112.7 0v.1a1.1 1.1 0 00.7 1 1.1 1.1 0 001.2-.2l.1-.1a1.3 1.3 0 111.9 1.9l-.1.1a1.1 1.1 0 00-.2 1.2v.1a1.1 1.1 0 001 .7h.2a1.3 1.3 0 110 2.7h-.1a1.1 1.1 0 00-1 .7z"/></svg>',
    help: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="10" cy="10" r="7.5"/><path d="M8.1 7.8a1.9 1.9 0 113.1 1.5c-.6.5-1.2.8-1.2 1.7" stroke-linecap="round"/><circle cx="10" cy="14" r=".8" fill="currentColor" stroke="none"/></svg>',
    diamond: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M10 2.6l7.4 7.4-7.4 7.4L2.6 10z"/></svg>',
    circleCheck: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="10" cy="10" r="8"/><path d="M6.6 10.2l2.3 2.3 4.6-4.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    circleQ: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="10" cy="10" r="8"/><path d="M8.1 8a1.9 1.9 0 113.1 1.5c-.6.5-1.2.8-1.2 1.7" stroke-linecap="round"/><circle cx="10" cy="14" r=".8" fill="currentColor" stroke="none"/></svg>',
    shield: '<svg width="19" height="19" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M10 2.2l6.2 2.3v5c0 3.6-2.5 6.9-6.2 8.3-3.7-1.4-6.2-4.7-6.2-8.3v-5z"/><path d="M7.2 9.9l2 2 3.6-3.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    dots: '<svg width="19" height="19" viewBox="0 0 20 20" fill="currentColor"><circle cx="4.5" cy="10" r="1.5"/><circle cx="10" cy="10" r="1.5"/><circle cx="15.5" cy="10" r="1.5"/></svg>',
    plus: '<svg width="19" height="19" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M10 4.5v11M4.5 10h11"/></svg>',
    caret: '<svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5.5 8l4.5 4.5L14.5 8"/></svg>',
    pen: '<svg width="19" height="19" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M3 14.2l8.6-8.6 3 3L6 17.2H3z"/><path d="M12.4 4.8l1.6-1.6 3 3-1.6 1.6"/></svg>',
    mic: '<svg width="19" height="19" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><rect x="7.6" y="2.4" width="4.8" height="9" rx="2.4"/><path d="M4.6 9.4a5.4 5.4 0 0010.8 0M10 14.8v2.8"/></svg>',
    homeI: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M3 9.2L10 3.4l7 5.8V16a1 1 0 01-1 1h-3.4v-4.4H7.4V17H4a1 1 0 01-1-1z"/></svg>',
    x: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M5.5 5.5l9 9M14.5 5.5l-9 9"/></svg>',
    play: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path d="M5.5 3.5l11 6.5-11 6.5z"/></svg>',
    pause: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><rect x="5" y="3.5" width="3.6" height="13" rx="1"/><rect x="11.4" y="3.5" width="3.6" height="13" rx="1"/></svg>',
    restart: '<svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3.4 10a6.6 6.6 0 1 0 2-4.7"/><path d="M3 3.2v3.4h3.4"/></svg>',
    skip: '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path d="M3.5 3.8l8 6.2-8 6.2z"/><rect x="13.2" y="3.8" width="2.6" height="12.4" rx="1"/></svg>',
    info: '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="10" cy="10" r="7.6"/><path d="M10 9.2v4.4" stroke-linecap="round"/><circle cx="10" cy="6.5" r=".85" fill="currentColor" stroke="none"/></svg>',
    ok: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 10.4l3.3 3.3 7.7-7.9"/></svg>',
    tick: '<svg width="10" height="10" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.4l3.6 3.6L16 5.4"/></svg>',
    ext: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M11.5 3.5H16v4.5M16 3.5l-6.4 6.4M13.6 11.4V15a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 15V7.9A1.5 1.5 0 015 6.4h3.6"/></svg>',
    copy: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35"><rect x="6.6" y="6.6" width="9.4" height="9.4" rx="2"/><path d="M13 4.4a2 2 0 00-2-2H5.6a2 2 0 00-2 2v5.4a2 2 0 002 2"/></svg>',
    up: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M6.2 17.4V9.2l3.6-6.4a1.7 1.7 0 012.4 1.9L11 8.3h4.4a1.8 1.8 0 011.7 2.2l-1.2 5a1.8 1.8 0 01-1.8 1.4H6.2z"/><rect x="2.6" y="9" width="3.6" height="8.4" rx="1"/></svg>',
    down: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M13.8 2.6v8.2l-3.6 6.4a1.7 1.7 0 01-2.4-1.9L9 11.7H4.6a1.8 1.8 0 01-1.7-2.2l1.2-5A1.8 1.8 0 015.9 3h7.9z"/><rect x="13.8" y="2.6" width="3.6" height="8.4" rx="1"/></svg>',
    clock: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M10 5.4V10l3 1.8"/></svg>',
    doc: '<svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M11.4 2.6H5.6a1.6 1.6 0 00-1.6 1.6v11.6a1.6 1.6 0 001.6 1.6h8.8a1.6 1.6 0 001.6-1.6V7.2z"/><path d="M11.4 2.6v4.6H16"/></svg>',
    spark: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="#6b5bb5" stroke-width="1.35" stroke-linejoin="round"><path d="M10 2.6l1.7 4.2 4.2 1.7-4.2 1.7L10 14.4l-1.7-4.2-4.2-1.7 4.2-1.7z"/>    <path d="M15.6 13.4l.7 1.7 1.7.7-1.7.7-.7 1.7-.7-1.7-1.7-.7 1.7-.7z"/></svg>',
        ctx: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M12 2.4H6.2a1.7 1.7 0 00-1.7 1.7v11.8a1.7 1.7 0 001.7 1.7h7.6a1.7 1.7 0 001.7-1.7V6z"/><path d="M12 2.4V6h3.5" stroke-linecap="round"/><path d="M7.4 10.4h5.2M7.4 13.4h3.4" stroke-linecap="round"/></svg>',
        upload: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14.2V3.4M6.2 7.2L10 3.4l3.8 3.8M3.4 17h13.2"/></svg>',
        cloud: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M6.1 15.4a3.4 3.4 0 01-.5-6.8 4.4 4.4 0 018.3-1.3 3.6 3.6 0 01.5 7.1z"/></svg>',
        bag: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><rect x="2.6" y="6.2" width="14.8" height="10.2" rx="2"/><path d="M7.2 6.2V5a1.6 1.6 0 011.6-1.6h2.4A1.6 1.6 0 0112.8 5v1.2M2.6 10.4h14.8" stroke-linecap="round"/></svg>',
        tickBlue: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.4l3.6 3.6L16 5.4"/></svg>',
        folder: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M2.6 6.2a1.4 1.4 0 011.4-1.4h3l1.5 1.7h6.9a1.4 1.4 0 011.4 1.4v6.5a1.4 1.4 0 01-1.4 1.4H4a1.4 1.4 0 01-1.4-1.4z"/></svg>',
        file: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M11.6 2.8H5.8a1.4 1.4 0 00-1.4 1.4v11.6a1.4 1.4 0 001.4 1.4h8.4a1.4 1.4 0 001.4-1.4V6.8z"/><path d="M11.6 2.8v4h4"/></svg>',
        checkThin: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.6l3.6 3.6L16.2 5"/></svg>',
        search: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round"><circle cx="8.8" cy="8.8" r="5.4"/><path d="M12.8 12.8l4 4"/></svg>',
        globe: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="10" cy="10" r="7.4"/><path d="M2.8 10h14.4M10 2.6a12 12 0 010 14.8A12 12 0 0110 2.6z"/></svg>',
        arrowR: '<svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M7.6 4.6l5.4 5.4-5.4 5.4"/></svg>',
        spinner: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" class="spin"><path d="M10 2.6a7.4 7.4 0 107.4 7.4" opacity=".85"/><path d="M17.4 10A7.4 7.4 0 0010 2.6" opacity=".2"/></svg>',
        hex: '<svg width="15" height="15" viewBox="0 0 20 20" fill="currentColor" class="spin"><path d="M10 1.8l7 4v8.4l-7 4-7-4V5.8z" opacity=".22"/><path d="M10 1.8l7 4-3.5 2-3.5-2z"/><path d="M3 5.8l3.5 2v4l-3.5 2z" opacity=".55"/></svg>',
        stop: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" fill="#1a1a1a"/><rect x="7" y="7" width="6" height="6" rx="1.2" fill="#fff"/></svg>',
        queue: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15.6V4.4M5.4 9L10 4.4 14.6 9"/></svg>',
        circleOpen: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="#c9c9c9" stroke-width="1.4"><circle cx="10" cy="10" r="7"/></svg>',
        circleDone: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="10" cy="10" r="7"/><path d="M6.9 10.2l2.1 2.1 4.2-4.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        circleNow: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="#c9c9c9" stroke-width="1.4" stroke-dasharray="3 2.6"><circle cx="10" cy="10" r="7"/></svg>',
        para: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><path d="M3 4.4h14M3 8h9M3 11.6h14M3 15.2h9"/></svg>',
        fmt: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15.6l5.6-11 5.6 11M6.2 12h6.8"/><path d="M15.4 3.6l1.6 1.6"/></svg>',
        table: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="2.8" y="3.6" width="14.4" height="12.8" rx="1.6"/><path d="M2.8 7.8h14.4M7.6 7.8v8.6M12.4 7.8v8.6"/></svg>',
        slide: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><rect x="2.6" y="4" width="14.8" height="10.4" rx="1.6"/><path d="M10 14.4v2.2M7.4 16.6h5.2"/></svg>',
        chart: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><path d="M3.4 16.6V9M8 16.6V4.6M12.6 16.6v-5M17 16.6V7.4"/></svg>',
        dl: '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M10 3v9M6.4 8.4L10 12l3.6-3.6M3.6 15.4h12.8"/></svg>',
        folderOpen: '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M2.6 15V5.4a1.3 1.3 0 011.3-1.3h3.2l1.5 1.7h6a1.3 1.3 0 011.3 1.3v1"/><path d="M2.6 15l1.9-6.2a1.2 1.2 0 011.15-.85h11.1a1 1 0 01.96 1.3L15.9 15z"/></svg>',
        sparkS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M9 3.4l1.4 3.4 3.4 1.4-3.4 1.4L9 13l-1.4-3.4L4.2 8.2l3.4-1.4z"/><path d="M14.6 12.6l.6 1.4 1.4.6-1.4.6-.6 1.4-.6-1.4-1.4-.6 1.4-.6z"/></svg>',
        wordS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="2.6" y="3.4" width="14.8" height="13.2" rx="2"/><path d="M5.6 7.4l1.6 5.2 1.8-4 1.8 4 1.6-5.2" stroke-linecap="round"/></svg>',
        pptS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="2.6" y="3.4" width="14.8" height="13.2" rx="2"/><path d="M7 13V7h2.6a2 2 0 010 4H7" stroke-linecap="round"/></svg>',
        spS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="7.4" cy="7.4" r="4.4"/><circle cx="12.8" cy="10.6" r="3.6" opacity=".65"/><circle cx="9.4" cy="14.2" r="2.8" opacity=".4"/></svg>',
        imgS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="2.6" y="4" width="14.8" height="12" rx="2"/><circle cx="7.2" cy="8.4" r="1.4"/><path d="M3.4 14.2l4-3.6 3.2 2.8 2.6-2.2 3.4 3"/></svg>',
        pdfS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M11.6 2.8H5.8a1.4 1.4 0 00-1.4 1.4v11.6a1.4 1.4 0 001.4 1.4h8.4a1.4 1.4 0 001.4-1.4V6.8z"/><path d="M11.6 2.8v4h4"/><path d="M6.8 13.4c2.2-.6 3.4-2.6 3.8-4.2.3 2 1.6 3.4 3 3.4" stroke-linecap="round"/></svg>',
        codeS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7.2 6.4L3.4 10l3.8 3.6M12.8 6.4L16.6 10l-3.8 3.6M11 4.2l-2 11.6"/></svg>',
        outlookS: '<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><rect x="1.6" y="4.4" width="9.4" height="11.2" rx="1.6" fill="#0f6cbd"/><ellipse cx="6.3" cy="10" rx="2.4" ry="2.9" fill="#fff"/><ellipse cx="6.3" cy="10" rx="1.1" ry="1.5" fill="#0f6cbd"/><path d="M11.6 6.6h6.2a.6.6 0 01.6.6v5.6a.6.6 0 01-.6.6h-6.2z" fill="#28a8ea"/><path d="M11.6 7.1l3.4 2.3 3.4-2.3" stroke="#fff" stroke-width="1"/></svg>',
        send: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M17.4 10L3.2 3.6l2.1 6.4-2.1 6.4z"/><path d="M5.3 10h12.1" stroke-linecap="round"/></svg>',
        bullet: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><path d="M7.4 5.6h9M7.4 10h9M7.4 14.4h9"/><circle cx="4" cy="5.6" r="1" fill="currentColor" stroke="none"/><circle cx="4" cy="10" r="1" fill="currentColor" stroke="none"/><circle cx="4" cy="14.4" r="1" fill="currentColor" stroke="none"/></svg>',
        numlist: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><path d="M7.4 5.6h9M7.4 10h9M7.4 14.4h9M3.2 4.4l1-.5v3M2.7 9.2c.2-.5 1.8-.7 1.8.3 0 .7-1.6 1.2-1.8 2.1h2M2.8 13.4h1.7l-1.1 1.2c.7 0 1.2.3 1.2.9s-.6 1-1.9.7"/></svg>',
        clip: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M14.6 9.2l-5 5a3 3 0 01-4.2-4.2l5.6-5.6a2 2 0 012.8 2.8l-5.6 5.6a1 1 0 01-1.4-1.4l5-5"/></svg>',
        rewrite: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M2.2 13.4L4.9 5.9l2.7 7.5M3.1 11h3.6"/><path d="M17.4 6.6l-6.5 6.5-2.6.6.6-2.6 6.5-6.5a1.4 1.4 0 012 2z"/></svg>',
        stopSq: '<svg width="15" height="15" viewBox="0 0 20 20" fill="currentColor"><rect x="5.6" y="5.6" width="8.8" height="8.8" rx="1.4"/></svg>',
        bulb: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"><path d="M7.6 15.2h4.8M8.4 17.2h3.2"/><path d="M10 2.8a5 5 0 00-3 9c.5.4.8 1 .8 1.6h4.4c0-.6.3-1.2.8-1.6a5 5 0 00-3-9z"/></svg>',
        iqS: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M4 6.2L10 3l6 3.2v7.6L10 17l-6-3.2z"/><path d="M10 3v14M4 6.2l6 3.4 6-3.4"/></svg>',
        props: '<svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="3" y="3" width="14" height="14" rx="2"/><path d="M6.4 7.4h7.2M6.4 10.4h7.2M6.4 13.4h4" stroke-linecap="round"/></svg>',
        newfile: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><path d="M11.4 2.8H5.8a1.4 1.4 0 00-1.4 1.4v11.6a1.4 1.4 0 001.4 1.4h8.4a1.4 1.4 0 001.4-1.4V6.8z"/><path d="M11.4 2.8v4h4M10 9.6v4.2M7.9 11.7h4.2" stroke-linecap="round"/></svg>',
        struct: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"><rect x="2.8" y="2.8" width="6" height="6" rx="1.2"/><rect x="11.2" y="2.8" width="6" height="6" rx="1.2"/><rect x="2.8" y="11.2" width="6" height="6" rx="1.2"/><rect x="11.2" y="11.2" width="6" height="6" rx="1.2"/></svg>',
        warn: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M10 3.2l7 12.4H3z"/><path d="M10 8v3.4" stroke-linecap="round"/><circle cx="10" cy="13.4" r=".8" fill="currentColor" stroke="none"/></svg>',
        mail: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="2.4" y="4.4" width="15.2" height="11.2" rx="1.6"/><path d="M2.4 6l7.6 5 7.6-5"/></svg>',
        cal: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="2.8" y="4" width="14.4" height="13" rx="1.8"/><path d="M2.8 8h14.4M6.6 2.4v3M13.4 2.4v3" stroke-linecap="round"/></svg>',
        teams: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><rect x="2.4" y="5.4" width="9" height="9" rx="1.6"/><path d="M4.4 8h5M6.9 8v4.2" stroke-linecap="round"/><circle cx="14.6" cy="6.4" r="2"/><path d="M12.4 14.6h3.6a1.6 1.6 0 001.6-1.6v-2.4a1.6 1.6 0 00-1.6-1.6h-2.4"/></svg>',
        graph: '<svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="5.2" cy="5.2" r="2.2"/><circle cx="14.8" cy="5.2" r="2.2"/><circle cx="10" cy="14.8" r="2.2"/><path d="M6.9 6.7l1.9 6M13.1 6.7l-1.9 6M7.4 5.2h5.2"/></svg>'
      };

  /* 홈 하단 타일 일러스트 */
  var ART = {
    inbox: '<svg width="60" height="52" viewBox="0 0 60 52" fill="none"><rect x="6" y="12" width="48" height="32" rx="5" fill="#eef1fb"/><path d="M6 17l24 15 24-15" stroke="#6b7fd7" stroke-width="2.2" stroke-linejoin="round"/><rect x="18" y="4" width="24" height="16" rx="3" fill="#fff" stroke="#c9a227" stroke-width="2"/><path d="M22 10h16M22 14h11" stroke="#c9a227" stroke-width="1.8" stroke-linecap="round"/></svg>',
    week: '<svg width="60" height="52" viewBox="0 0 60 52" fill="none"><rect x="5" y="8" width="18" height="18" rx="3" fill="#f2c94c"/><rect x="26" y="8" width="18" height="18" rx="3" fill="#4a5568"/><rect x="15" y="28" width="18" height="18" rx="3" fill="#56c596"/><rect x="36" y="28" width="18" height="18" rx="3" fill="#7b8cde"/></svg>',
    meet: '<svg width="60" height="52" viewBox="0 0 60 52" fill="none"><path d="M30 12c-6-5-14-5-19-2v30c5-3 13-3 19 2z" fill="#c9b6ec"/><path d="M30 12c6-5 14-5 19-2v30c-5-3-13-3-19 2z" fill="#f2c94c"/><path d="M30 12v30" stroke="#fff" stroke-width="2"/></svg>'
  };

  function esc(s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
    });
  }
  /* 굵게, 코드, 파이프 표만 지원한다. 실제 답변에 이 셋이 나온다. */
  function rich(s) {
    var inline = function (t) {
      return esc(t)
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');
    };
    var cells = function (line) {
      return line.replace(/^\s*\|/, '').replace(/\|\s*$/, '').split('|')
        .map(function (c) { return c.trim(); });
    };
    return s.split(/\n{2,}/).map(function (p) {
      var lines = p.split('\n');
      var isTable = lines.length > 2 && lines.every(function (l) { return /^\s*\|/.test(l); });
      if (isTable) {
        var head = cells(lines[0]);
        var body = lines.slice(2).map(cells);
        return '<table><thead><tr>' +
          head.map(function (c) { return '<th>' + inline(c) + '</th>'; }).join('') +
          '</tr></thead><tbody>' +
          body.map(function (r) {
            return '<tr>' + r.map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>';
          }).join('') + '</tbody></table>';
      }
      if (lines.every(function (l) { return /^\s*[-·]\s+/.test(l); })) {
        return '<ul>' + lines.map(function (l) {
          return '<li>' + inline(l.replace(/^\s*[-·]\s+/, '')) + '</li>';
        }).join('') + '</ul>';
      }
      if (lines.length === 1 && /^#{2,4}\s+/.test(lines[0])) {
        return '<h4>' + inline(lines[0].replace(/^#+\s+/, '')) + '</h4>';
      }
      return '<p>' + lines.map(inline).join('<br>') + '</p>';
    }).join('');
  }
  function el(h) { var d = document.createElement('div'); d.innerHTML = h.trim(); return d.firstElementChild; }
  function scroll() { if (stream) { stream.scrollTop = stream.scrollHeight; } }

  /* ── 팝오버 ──
     실제 화면의 ＋ 메뉴, 모델 선택기, 노력 선택기를 재현한다.
     데모이므로 첨부 항목은 열리기만 하고 동작하지 않는다. */
  var PLUS_MENU = [
    { ic: 'ctx', t: '작업 컨텍스트 추가', s: '파일, 사람, 모임', k: 'Ctrl+/' },
    { ic: 'upload', t: '이미지 및 파일 업로드', s: 'PDF, Word, Excel, 이미지', k: 'Ctrl+U' },
    { ic: 'cloud', t: '클라우드 파일 및 폴더 첨부', s: 'OneDrive, SharePoint, Teams', k: 'Ctrl+Shift+U' },
    { sep: true },
    { ic: 'bag', t: '사용자 지정', s: '기술 및 플러그인 관리' }
  ];
  var EFFORT = [
    { t: '가벼움', s: '빠른 응답. 단순한 작업' },
    { t: '보통', s: '균형. 대부분의 작업' },
    { t: '높음', s: '더 깊이 생각. 복잡한 분석' },
    { t: '매우 높음', s: '가장 깊이 생각. 장시간 조사와 다단계 작업' }
  ];

  /* 입력창 아래 팁은 실제 화면에서 여러 개가 번갈아 나온다. */
  var TIPS = [
    ['Ctrl+Shift+U', '을(를) 눌러 OneDrive 또는 SharePoint의 파일을 첨부하세요.'],
    ['Ctrl+U', '을(를) 눌러 디바이스에서 이미지와 파일을 업로드하세요.'],
    ['/', '을 눌러 M365 파일, 사용자, 기술 등에서 선택하세요.']
  ];
  var tipN = 0;

  /* 모델을 바꾸면 노력 기본값이 따라 바뀐다.
     GPT 계열은 매우 높음, Claude 계열과 자동은 보통이 기본이다. */
  function defaultEffort(model) {
    return /^GPT/i.test(model) ? '매우 높음' : '보통';
  }

  function closePops(except) {
    [].forEach.call(document.querySelectorAll('.pop'), function (p) {
      if (p !== except) {
        p.classList.remove('on');
        var t = p.previousElementSibling;
        if (t) { t.setAttribute('aria-expanded', 'false'); }
      }
    });
  }

  /* label: 버튼에 보일 내용, items: 메뉴 항목, onPick: 선택 콜백 */
  function popover(label, items, opts) {
    opts = opts || {};
    var wrap = el('<span class="pop-wrap"></span>');
    var btn = el('<button class="pill" aria-expanded="false">' + label + '</button>');
    var pop = el('<div class="pop' + (opts.narrow ? ' narrow' : '') + (opts.up ? ' up' : '') + '"></div>');

    items.forEach(function (m) {
      if (m.sep) { pop.appendChild(el('<div class="sep"></div>')); return; }
      var mi = el('<button class="mi">' +
        (m.ic ? '<span class="mic-ic">' + I[m.ic] + '</span>' : '') +
        '<span class="mtx"><span class="mt">' + esc(m.t) + '</span>' +
        (m.s ? '<span class="ms">' + esc(m.s) + '</span>' : '') + '</span>' +
        (m.k ? '<span class="kb">' + esc(m.k) + '</span>' : '') +
        (opts.check ? '<span class="tickmark">' + (m.t === opts.current ? I.tickBlue : '') + '</span>' : '') +
        '</button>');
      mi.addEventListener('click', function (e) {
        e.stopPropagation();
        closePops();
        if (opts.onPick) { opts.onPick(m.t); }
      });
      pop.appendChild(mi);
    });

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var on = pop.classList.contains('on');
      closePops();
      if (!on) { pop.classList.add('on'); btn.setAttribute('aria-expanded', 'true'); }
    });
    wrap.appendChild(btn);
    wrap.appendChild(pop);
    return wrap;
  }

  /* 모델 목록은 실제 Cowork 선택기와 같다. 이 시나리오에서 측정한 회차가 있으면
     설명 줄에 실측 크레딧을 덧붙이고, 없으면 측정하지 않았다고 밝힌다. */
  var MODEL_LIST = [
    ['자동', '작업에 맞는 모델을 고릅니다'],
    ['Claude Sonnet 5', 'Claude 계열 · 기본 노력 보통'],
    ['Claude Opus 5', 'Claude 계열 · 기본 노력 보통'],
    ['GPT 5.6 Terra', 'GPT 계열 · 기본 노력 매우 높음'],
    ['GPT 5.6 Sol', 'GPT 계열 · 기본 노력 매우 높음']
  ];

  /* 컴포저 한 줄을 만든다. run이 있으면 모델·노력이 실제 데이터와 연동된다. */
  function composerRow(host, live) {
    host.innerHTML = '';
    host.appendChild(popover(I.plus, PLUS_MENU, { up: !live }));

    var models = MODEL_LIST.map(function (m) {
      var hit = live && run.bench.models.filter(function (x) { return x.name === m[0]; })[0];
      return { t: m[0], s: hit ? '이 시나리오 실측 ' + fmt(Math.round(hit.avg)) + ' 크레딧' : m[1] };
    });
    if (!live) { models = [{ t: '자동', s: '작업에 맞는 모델을 고릅니다' }]; }
    if (live && !models.some(function (m) { return m.t === run.model; })) {
      models.unshift({ t: run.model, s: '이번 실행에 쓴 모델' });
    }
    var curModel = live ? (picked || run.model) : '자동';

    var mWrap = popover('<span id="mdlLabel">' + esc(curModel) + '</span> ' + I.caret, models, {
      narrow: true, check: true, current: curModel, up: !live,
      onPick: function (name) {
        if (live) {
          picked = name;
          effortPick = defaultEffort(name);
          if (costShown) { redrawCost(); }
          rebuildComposer();
        } else {
          var lab = document.getElementById('mdlLabel');
          if (lab) { lab.textContent = name; }
          var el2 = document.getElementById('effLabel');
          if (el2) { el2.textContent = defaultEffort(name); }
        }
      }
    });
    host.appendChild(mWrap);

    var curEffort = live ? (effortPick || run.effort) : '보통';
    host.appendChild(popover('<span id="effLabel">' + esc(curEffort) + '</span> ' + I.caret, EFFORT, {
      narrow: true, check: true, current: curEffort, up: !live,
      onPick: function (t) {
        if (live) { effortPick = t; }
        var lab = document.getElementById('effLabel');
        if (lab) { lab.textContent = t; }
      }
    }));

    host.appendChild(el('<span class="spacer"></span>'));
    /* 오른쪽 묶음. 실제 화면은 다듬기 아이콘과 원형 마이크만 두고,
       보낼 내용이 있을 때만 검은 원형 보내기가 붙는다.
       재생 중에는 검은 원형이 중지로 바뀌고 회색 대기열 pill이 따라온다. */
    host.appendChild(el('<button class="pill" title="다시 쓰기">' + I.rewrite + '</button>'));
    host.appendChild(el('<button class="micb" title="받아쓰기">' + I.mic + '</button>'));
    if (live && running) {
      host.appendChild(el('<button class="rnd stop" title="중지">' + I.stopSq + '</button>'));
      host.appendChild(el('<button class="qbtn" disabled>' + I.up + '대기열</button>'));
    }
  }

  /* 재생 중에는 실제 화면처럼 입력창 문구와 오른쪽 버튼이 바뀐다. */
  function setRunningUI(on) {
    running = on;
    var ph = document.getElementById('cph');
    if (ph) { ph.textContent = on ? '처리 중입니다. 다음 단계는 무엇일까요?' : 'Cowork에 메시지 보내기'; }
    rebuildComposer();
  }

  function rebuildComposer() {
    var host = document.getElementById('crow');
    if (host) { composerRow(host, true); }
  }

  /* ── 사이드바 ── */
  /* 목록은 실제 화면의 밀도만 흉내 낸 예시 항목이다.
     고객에게 나가는 자료이므로 회사명, 고객사명, 사내 프로젝트명을 쓰지 않는다. */
  var FILLER = [
    ['주간 업무보고 자동 생성', 0, ''],
    ['한국어 문서 교정 지원 요청', 0, 'help'],
    ['PDF 문서에 민감도 레이블 적용', 0, ''],
    ['Microsoft 365 Copilot 활용 범위 …', 1, ''],
    ['분기 실적 자료 초안 작성', 0, ''],
    ['SharePoint 문서 검색 방법 문의', 1, 'help'],
    ['회의록 정리 및 액션아이템 추출', 0, ''],
    ['노트북 사양 확인 및 조회', 1, ''],
    ['보고서 표 형식 통일 요청', 0, ''],
    ['포커스 시간 설정 방법 안내', 0, ''],
    ['워크숍용 프롬프트 목록 정리', 0, ''],
    ['크레딧 사용량 확인 방법', 0, ''],
    ['일정 조율 및 회의실 예약', 1, '']
  ];

  function buildSide() {
    document.getElementById('sideTop').innerHTML =
      '<span class="brand">Copilot</span><div class="side-icons">' +
      '<button class="ib">' + I.grid + '</button>' +
      '<button class="ib">' + I.check + '</button>' +
      '<button class="ib">' + I.panel + '</button></div>';

    document.getElementById('nav').innerHTML =
      '<button class="newtask" id="btNew"><span class="ic">' + I.plusC + '</span>새 작업</button>' +
      '<button><span class="ic">' + I.tasks + '</span>내 작업</button>' +
      '<button><span class="ic">' + I.bolt + '</span>자동화</button>' +
      '<button><span class="ic">' + I.brain + '</span>사용자 지정</button>';
    document.getElementById('btNew').addEventListener('click', renderHome);

    var box = document.getElementById('chats');
    box.innerHTML = '';
    RUNS.forEach(function (r) {
      var b = el('<button data-id="' + r.id + '"><span class="lbl">' + esc(r.chatTitle || r.title) + '</span></button>');
      b.addEventListener('click', function () { open(r.id); });
      box.appendChild(b);
    });
    FILLER.forEach(function (f) {
      var b = el('<button class="' + (f[1] ? 'dim' : '') + '"><span class="lbl">' + esc(f[0]) + '</span>' +
        (f[2] ? '<span class="rt">' + I.help + '</span>' : '') + '</button>');
      b.addEventListener('click', renderHome);
      box.appendChild(b);
    });

    document.getElementById('me').innerHTML =
      '<div class="av">CU</div><div>' +
      '<div class="nm"><span class="tag">작업</span><b>Copilot User</b></div>' +
      '<div class="sub">M365 Copilot(프리미엄)</div></div>' +
      '<button class="ib gear">' + I.gear + '</button>';
  }

  function markSide(id) {
    [].forEach.call(document.querySelectorAll('#chats button'), function (b) {
      b.classList.toggle('on', b.dataset.id === id);
    });
  }

  /* ── 홈 ── */
  function renderHome() {
    document.title = 'Copilot Cowork 시나리오 데모';
    app.classList.remove('panel-open');
    /* 팁은 실제 화면처럼 열 때마다 바뀐다. */
    var tip = TIPS[tipN % TIPS.length];
    tipN++;

    var resume = RUNS.map(function (r) {
      var chips = r.artifacts.slice(0, 1).map(function (a) { return fileChip(a.name); }).join('');
      var extra = r.artifacts.length > 1 ? '<span class="plus">+' + (r.artifacts.length - 1) + '</span>' : '';
      return '<button class="ritem" data-id="' + r.id + '">' +
        '<span class="rico">' + I.circleCheck + '</span>' +
        '<span class="rbody"><span class="rtitle">' + esc(r.chatTitle || r.title) + '</span>' +
        '<span class="rsub">' + esc(r.subtitle) + '</span></span>' +
        '<span class="rchips">' + chips + extra + '</span></button>';
    }).join('');

    document.getElementById('main').innerHTML =
      '<div class="mtop"><div class="right">' +
        '<button class="ib shield">' + I.shield + '</button>' +
        '<button class="ib">' + I.dots + '</button></div></div>' +
      '<div class="home-wrap"><div class="home-in">' +
        '<h1 class="hero-q">지금 무엇을 작업하고 있나요?</h1>' +
        '<div class="inputbox">' +
          '<div class="ph">작업 시작…</div>' +
          '<div class="crow" id="homeCrow"></div>' +
        '</div>' +
        '<div class="tipline"><span class="ti">' + I.bulb + '</span>팁: <kbd>' +
          esc(tip[0]) + '</kbd> ' + esc(tip[1]) + '</div>' +
        '<div class="sec-h">다음 재생 항목<span class="more">더 보기</span></div>' +
        '<div class="resume" id="resume">' + resume +
          (RUNS.length >= 3 ? '' :
          '<button class="ritem" id="fillA"><span class="rico">' + I.circleQ + '</span>' +
          '<span class="rbody"><span class="rtitle">한국어 문서 교정 지원 요청</span>' +
          '<span class="rsub">Checking your document for corrections</span></span></button>' +
          '<button class="ritem" id="fillB"><span class="rico">' + I.circleCheck + '</span>' +
          '<span class="rbody"><span class="rtitle">PDF 문서에 민감도 레이블 적용</span></span></button>') +
        '</div>' +
        '<div class="sec-h">다음에 이걸 시도해 보세요.<span class="more">더 보기</span></div>' +
        '<div class="tiles">' +
          '<button class="tile"><div class="art">' + ART.inbox + '</div>' +
            '<div class="tl">받은 편지함 정리</div><div class="ts">평균 178 크레딧</div></button>' +
          '<button class="tile"><div class="art">' + ART.week + '</div>' +
            '<div class="tl">내 주 정렬</div><div class="ts">평균 393 크레딧</div></button>' +
          '<button class="tile"><div class="art">' + ART.meet + '</div>' +
            '<div class="tl">모임 준비</div><div class="ts">평균 767 크레딧</div></button>' +
        '</div>' +
      '</div></div>';

    [].forEach.call(document.querySelectorAll('.ritem[data-id]'), function (b) {
      b.addEventListener('click', function () { open(b.dataset.id); });
    });
    composerRow(document.getElementById('homeCrow'), false);
    markSide(null);
  }

  /* ── 실행 화면 ── */
  function open(id) {
    run = RUNS.filter(function (r) { return r.id === id; })[0];
    if (!run) { return renderHome(); }
    document.title = run.title + ' · Copilot Cowork 데모';
    app.classList.add('panel-open');
    idx = 0; costShown = false;
    clearInterval(timer); timer = null;

    document.getElementById('main').innerHTML =
      '<div class="mtop bordered">' +
        '<button class="home" id="goHome">' + I.homeI + '</button>' +
        '<div class="tb-title"><h1>' + esc(run.chatTitle || run.title) + '</h1>' +
        '<div class="sub">' + esc(run.model) + ' · ' + esc(run.effort) + ' · ' + esc(run.tc) + '</div></div>' +
        '<div class="right">' +
          '<button class="ib shield">' + I.shield + '</button>' +
          '<button class="ib" id="tgPanel">' + I.panel + '</button>' +
          '<button class="ib">' + I.dots + '</button>' +
        '</div></div>' +
      '<div class="ctrl">' +
        '<button class="btn primary" id="play">' + I.play + '<span>재생</span></button>' +
        '<button class="btn" id="restart">' + I.restart + '처음부터</button>' +
        '<button class="btn" id="skip">' + I.skip + '끝으로</button>' +
        '<div class="speed"><span>속도</span>' +
          '<input type="range" id="sp" min="1" max="6" step="1" value="2">' +
          '<span class="v" id="spv">2×</span></div>' +
        '<div class="prog"><i id="bar"></i></div>' +
        '<div class="count" id="cnt">0/' + (run.log.length + 1) + '</div>' +
      '</div>' +
      '<div class="notice"><span class="ic">' + I.info + '</span><span>' +
        '실제 실행 기록입니다. 개인정보는 마스킹했고, 크레딧은 <code>/cost</code> 실측값입니다.' +
        (run.note ? ' <b>볼 것</b> — ' + esc(run.note) : '') + '</span></div>' +
      '<div class="stream" id="stream"><div class="wrap" id="w">' +
        '<div class="daysep"><span>' + esc(run.date) + ' · KST</span></div></div></div>' +
      '<div class="composer"><div class="cbox">' +
        '<div class="ph" id="cph">Cowork에 메시지 보내기</div>' +
        '<div class="crow" id="crow"></div>' +
        '<div class="foot">AI 생성 콘텐츠는 정확하지 않을 수 있습니다</div>' +
      '</div></div>';

    stream = document.getElementById('stream');
    picked = run.model;
    effortPick = run.effort;
    renderPanel();
    composerRow(document.getElementById('crow'), true);

    document.getElementById('goHome').addEventListener('click', renderHome);
    document.getElementById('tgPanel').addEventListener('click', function () { app.classList.toggle('panel-open'); });
    document.getElementById('play').addEventListener('click', toggle);
    document.getElementById('restart').addEventListener('click', function () { open(id); });
    document.getElementById('skip').addEventListener('click', skipAll);
    document.getElementById('sp').addEventListener('input', function (e) {
      speed = +e.target.value;
      document.getElementById('spv').textContent = speed + '×';
      if (timer) { start(); }
    });

    var ub = userBubble(run.prompt, run.promptTime, run.promptFiles, true);
    document.getElementById('w').appendChild(ub);
    markSide(id);
    tick();
  }

  /* 사용자 프롬프트 말풍선. 같은 작업에서 이어 시키면 두 번째부터 로그 중간에 낀다.
     여섯 줄이 넘으면 접고 "더 보기"를 붙인다. */
  function userBubble(text, time, files, first) {
    var lines = (text || '').split('\n');
    var headTxt = lines.slice(0, 6).join('\n');
    var restTxt = lines.slice(6).join('\n');
    var node = el('<div class="uwrap"><div class="ubox">' +
      ((files || []).length
        ? '<div class="uatt">' + files.map(fileChip).join('') + '</div>' : '') +
      '<div class="ubub"><span class="ptxt"' + (first ? ' id="ptxt"' : '') + '>' +
      esc(headTxt) + '</span>' +
      (restTxt ? '<span class="prest"' + (first ? ' id="prest"' : '') + ' hidden>' +
        esc('\n' + restTxt) + '</span>' : '') +
      (restTxt ? '<button class="fold"' + (first ? ' id="pfold"' : '') + '>더 보기</button>' : '') +
      '</div>' +
      '<div class="umeta"><span>' + esc(time) + '</span>' +
      '<button title="복사">' + I.copy + '</button>' +
      '<span class="num">99</span></div>' +
      '</div></div>');
    var fold = node.querySelector('.fold');
    if (fold) {
      fold.addEventListener('click', function () {
        var r = node.querySelector('.prest');
        if (r.hasAttribute('hidden')) { r.removeAttribute('hidden'); this.textContent = '간단히 보기'; }
        else { r.setAttribute('hidden', ''); this.textContent = '더 보기'; }
      });
    }
    return node;
  }

  /* ── 작업 영역 ── */
  var TOOLICO = { 'SharePoint': 'spS', 'Web Search': 'globe', 'Work IQ': 'iqS',
                  'Outlook': 'mail', '일정': 'cal', 'Teams': 'teams',
                  'Microsoft Graph': 'graph' };
  var TOOLDESC = {
    'SharePoint': '이 작업에 대해 파일 및 문서를 사용함',
    'Web Search': '이 작업에 대해 웹을 검색함',
    'Work IQ': '이 작업에 대해 조직의 콘텐츠를 검색함',
    'Outlook': '이 작업에 대해 Outlook 메일 또는 일정을 사용함',
    '일정': '이 작업에 대해 달력 이벤트 및 일정을 사용함',
    'Teams': '이 작업에 대해 Teams 채팅, 채널 또는 모임을 사용함',
    'Microsoft Graph': '이 작업에 Microsoft Graph 데이터를 사용함'
  };
  var SKILLDESC = {
    '깊이 탐구하기': '정보를 조사하고 종합합니다',
    'Word': '문서를 만들고 편집합니다',
    'PowerPoint': '프레젠테이션을 만들고 편집합니다',
    'Excel': '스프레드시트를 만들고 편집합니다',
    '이미지 작업': '이미지를 만들고 편집합니다',
    'PDF': 'PDF를 읽고 내용을 추출합니다',
    '콘텐츠 만들기': '문서, 프레젠테이션, 스프레드시트 및 기타 콘텐츠를 만듭니다',
    'html': 'HTML 파일을 만들고 편집합니다',
    'frontend-design': '이 작업에 대해 사용자 지정 기술을 사용함'
  };
  var SKILLICO = { '깊이 탐구하기': 'sparkS', 'Word': 'wordS', 'PowerPoint': 'pptS',
                   'Excel': 'spS', '이미지 작업': 'imgS', 'PDF': 'pdfS',
                   '콘텐츠 만들기': 'newfile', 'html': 'codeS',
                   'frontend-design': 'brain' };

  function tagList(names, ico, desc) {
    return names.map(function (s) {
      return '<span class="tag" title="' + esc(desc[s] || '') + '">' +
        '<span class="tgi">' + (I[ico[s]] || '') + '</span>' + esc(s) + '</span>';
    }).join('');
  }

  /* 파일 칩. 확장자로 아이콘 색을 정한다. */
  function fileKind(name) {
    if (/\.pptx?$/i.test(name)) { return 'p'; }
    if (/\.pdf$/i.test(name)) { return 'f'; }
    if (/\.html?$/i.test(name)) { return 'h'; }
    if (/\.xlsx?$|\.xltx$|\.csv$/i.test(name)) { return 'x'; }
    if (/\.(docx?|dotx)$/i.test(name)) { return 'w'; }
    return 'm';  /* 확장자가 없으면 메일 초안으로 본다 */
  }
  var KINDCH = { w: 'W', p: 'P', f: 'F', h: I.globe, x: 'X', m: I.mail };

  function fileChip(name) {
    var k = fileKind(name);
    return '<span class="chipf"><span class="fi ' + k + '">' + KINDCH[k] + '</span>' +
      '<span class="nm">' + esc(name) + '</span></span>';
  }

  function renderPanel() {
    /* 실제 화면도 내용이 없는 섹션은 아예 그리지 않는다.
       짧은 작업은 단계 계획을 세우지 않아 단계 칸 자체가 없다. */
    document.getElementById('panel').innerHTML =
      '<div class="p-top"><h2>작업 영역</h2><button class="ib x" id="pClose">' + I.x + '</button></div>' +
      '<div class="p-act" id="pAct" hidden></div>' +
      (run.steps.length
        ? '<div class="p-sec"><div class="p-h">단계 <span class="n" id="stepn">0/' + run.steps.length + '</span>' +
          '<span>' + I.caret + '</span></div>' +
          '<ul class="steps" id="steps">' + run.steps.map(function (s) {
            return '<li><span class="mk">' + I.circleOpen + '</span>' +
              '<span class="sx"><span class="st">' + esc(s) + '</span>' +
              '<span class="ss">보류 중</span></span></li>';
          }).join('') + '</ul></div>'
        : '') +
      (run.artifacts.length
        ? '<div class="p-sec"><div class="p-h">출력' +
          '<span class="acts"><button title="모두 다운로드">' + I.dl + '</button>' +
          '<button title="폴더 열기">' + I.folderOpen + '</button>' +
          '<button>' + I.caret + '</button></span></div>' +
          '<ul class="outs" id="outs"></ul></div>'
        : '') +
      /* 첨부한 파일이 있으면 참조 섹션이 붙는다. */
      ((run.refs || []).length
        ? '<div class="p-sec"><div class="p-h">참조 <span class="acts"><button>' + I.caret + '</button></span></div>' +
          '<ul class="outs">' + run.refs.map(function (n) {
            var k = fileKind(n);
            return '<li><span class="fi ' + k + '">' + KINDCH[k] + '</span>' +
              '<span class="nm">' + esc(n) + '</span></li>';
          }).join('') + '</ul></div>'
        : '') +
      ((run.skills || []).length || run.skillsButton
        ? '<div class="p-sec"><div class="p-h">기술 및 플러그 인 <span class="acts"><button>' + I.caret + '</button></span></div>' +
          '<div class="tags">' + tagList(run.skills || [], SKILLICO, SKILLDESC) +
          (run.skillsButton
            ? '<button class="tag mng"><span class="tgi">' + I.brain + '</span>기술 관리</button>'
            : '') + '</div></div>'
        : '') +
      ((run.tools || []).length
        ? '<div class="p-sec"><div class="p-h">도구 <span class="acts"><button>' + I.caret + '</button></span></div>' +
          '<div class="tags">' + tagList(run.tools, TOOLICO, TOOLDESC) + '</div></div>'
        : '');
    document.getElementById('pClose').addEventListener('click', function () {
      app.classList.remove('panel-open');
    });
  }

  /* 작업 영역 상단의 현재 활동 문구. 실제 화면에도 같은 자리에 뜬다. */
  function setPanelAct(text) {
    var a = document.getElementById('pAct');
    if (!a) { return; }
    if (text) { a.textContent = text; a.removeAttribute('hidden'); }
    else { a.setAttribute('hidden', ''); }
  }

  function syncPanel() {
    var total = run.log.length;
    var done = Math.min(run.steps.length, Math.floor(idx / total * run.steps.length));
    if (idx >= total) { done = run.steps.length; }
    if (idx >= total && run.stepStates) {
      done = run.stepStates.filter(function (x) { return x === '완료됨'; }).length;
    }
    var lis = document.getElementById('steps');
    lis = lis ? lis.children : [];
    var fin = run.stepStates || [];
    for (var i = 0; i < lis.length; i++) {
      var st = i < done ? 'done' : (i === done && idx < total ? 'now' : '');
      /* 재생이 끝난 뒤에는 실제 실행에서 남은 상태를 그대로 쓴다. 취소된 단계가 있다. */
      var lab = st === 'done' ? '완료됨' : (st === 'now' ? '진행 중' : '보류 중');
      if (idx >= total && fin[i]) {
        lab = fin[i];
        st = fin[i] === '완료됨' ? 'done' : (fin[i] === '진행 중' ? 'now' : 'off');
      }
      lis[i].className = st;
      lis[i].querySelector('.mk').innerHTML =
        st === 'done' ? I.circleDone : (st === 'now' ? I.circleNow : I.circleOpen);
      lis[i].querySelector('.ss').textContent = lab;
    }
    var sn = document.getElementById('stepn');
    if (sn) { sn.textContent = done + '/' + run.steps.length; }

    var outs = document.getElementById('outs');
    if (outs && idx >= total && !outs.children.length) {
      /* 실제 화면처럼 출력 항목을 눌러 바로 열 수 있게 한다. */
      run.artifacts.forEach(function (a, i) {
        var k = fileKind(a.name);
        var li = el('<li class="outrow"><button class="outbtn"><span class="fi ' + k + '">' + KINDCH[k] +
          '</span><span class="nm">' + esc(a.name) + '</span>' +
          '<span class="oo">' + I.ext + '</span></button></li>');
        li.querySelector('.outbtn').addEventListener('click', function () { viewer(i); });
        outs.appendChild(li);
      });
    }
  }

  /* ── 로그 한 줄 ──
     실제 화면 구조를 따른다. 어시스턴트 메시지에 아바타가 없고,
     도구 호출은 아이콘 + 회색 동사 + 굵은 대상으로 한 줄씩 흐른다. */
  var TOOLICON = { folder: 'folder', file: 'file', check: 'checkThin', search: 'search',
                   web: 'globe', newfile: 'newfile', struct: 'struct', warn: 'warn',
                   mail: 'mail', pen: 'pen', copy: 'copy' };

  function toolLine(t) {
    /* 묶음 안에 사고 과정이 섞여 나온다. 실제 화면도 도구 줄 사이에 그대로 낀다. */
    if (t.think) {
      return '<details class="think inner"><summary>' +
        '<span class="dot"></span><span>' + esc(t.label || '사고 과정') + '</span>' +
        '<span class="ar">' + I.arrowR + '</span></summary>' +
        '<div class="tbody">' + esc(t.body) + '</div></details>';
    }
    var ic = I[TOOLICON[t.icon] || 'checkThin'];
    var body = t.target
      ? esc(t.label) + ' <b>' + esc(t.target) + '</b>'
      : esc(t.label);
    return '<div class="tool' + (t.icon === 'check' ? ' done' : '') +
      (t.icon === 'warn' ? ' failed' : '') + '">' +
      '<span class="ti">' + ic + '</span><span>' + body + '</span>' +
      (t.tag ? '<span class="ttag' + (t.icon === 'warn' ? ' fail' : '') + '">' +
        esc(t.tag) + '</span>' : '') + '</div>';
  }

  function emit(s) {
    var w = document.getElementById('w'), node;

    if (s.t === 'say' || s.t === 'final') {
      node = el('<div class="turn"><div class="asay">' + rich(s.body) + '</div>' +
        (s.t === 'final' ? '<div class="fin"></div>' : '') + '</div>');

    } else if (s.t === 'think') {
      node = el('<details class="think"><summary>' +
        '<span class="dot"></span><span>' + esc(s.label || '사고 과정') + '</span>' +
        '<span class="ar">' + I.arrowR + '</span></summary>' +
        '<div class="tbody">' + esc(s.body) + '</div></details>');

    } else if (s.t === 'tool') {
      node = el(toolLine(s));

    } else if (s.t === 'tools') {
      /* 여러 도구 호출을 접어 보여준다. 3개까지 펼치고 나머지는 더 보기. */
      var head = (s.items || []).slice(0, 3).map(toolLine).join('');
      var rest = (s.items || []).slice(3).map(toolLine).join('');
      node = el('<details class="tgroup" open><summary>' +
        '<span>' + esc(s.label || '작업을 실행하는 중…') + '</span>' +
        '<span class="ar">' + I.caret + '</span></summary>' +
        '<div class="glist">' + head +
        (rest ? '<div class="grest" hidden>' + rest + '</div>' +
                '<button class="gmore">더 보기</button>' : '') +
        '</div></details>');
      var more = node.querySelector('.gmore');
      if (more) {
        more.addEventListener('click', function (e) {
          e.preventDefault();
          var r = node.querySelector('.grest');
          if (r.hasAttribute('hidden')) { r.removeAttribute('hidden'); this.textContent = '간단히 보기'; }
          else { r.setAttribute('hidden', ''); this.textContent = '더 보기'; }
        });
      }

    } else if (s.t === 'search') {
      /* 웹 검색. 실제 화면은 쿼리별 결과 수와 URL 목록을 함께 보여준다. */
      var total = (s.queries || []).reduce(function (n, q) { return n + (q.urls || []).length; }, 0);
      node = el('<details class="websearch" open><summary>' +
        '<span>' + I.globe + '</span>' +
        '<span>웹에서 검색함, 결과 ' + total + '개 찾음</span>' +
        '<span class="ar">' + I.caret + '</span></summary>' +
        (s.queries || []).map(function (q) {
          return '<div class="wq"><div class="q"><span>' + I.search + '</span>' +
            '<span><b>' + esc(q.q) + '</b> 검색함, 결과 ' + (q.urls || []).length + '개</span></div>' +
            '<div class="urls">' + (q.urls || []).map(function (u) {
              return '<a href="#" onclick="return false">' + esc(u) + '</a>';
            }).join('') + '</div></div>';
        }).join('') +
        '</details>');

    } else if (s.t === 'find') {
      node = el('<div class="find"><span class="ti">' + I.search + '</span>' +
        '<span><b>' + esc(s.q) + '</b> 검색 중</span>' +
        '<span class="srcs">' + (s.sources || []).map(function (x) {
          return '<span>' + esc(x) + '</span>';
        }).join('') + '</span></div>');

    } else if (s.t === 'edit') {
      /* 문서 편집. 실제 화면은 테두리 없이 흐르고, 같은 종류가 연달아 나오면
         "종류 [N] ⌄"로 묶여 접힌다. 실패는 파일 아이콘의 붉은 배지로 표시된다. */
      var EI = { '단락 삽입': 'para', '텍스트 서식 지정': 'fmt', '테이블 삽입': 'table',
                 '슬라이드 추가': 'slide', '차트 삽입': 'chart',
                 '단락 스타일 설정': 'fmt', '단락 텍스트 설정': 'para',
                 'Set doc properties': 'props', '문서 속성 설정': 'props',
                 '테이블 셀 설정': 'table', 'Set table column width': 'table',
                 '테이블 열 너비 설정': 'table',
                 '섹션 추가': 'slide', '간트 삽입': 'chart', '스타일 적용': 'fmt' };
      var items = s.items || [];

      var body = function (e) {
        if (e.size) { return '<span class="en2">· ' + esc(e.size) + '</span>'; }
        if (e.v) { return '<span class="ev">' + esc(e.v) + '</span>'; }
        return '';
      };
      var one = function (e) {
        return '<div class="eitem"><span class="ei">' + (I[EI[e.k] || 'para']) + '</span>' +
          '<span class="ek">' + esc(e.k) + '</span>' + body(e) + '</div>';
      };

      /* 같은 종류가 연달아 2개 이상이면 하나로 묶는다. */
      var blocks = [], i2 = 0;
      while (i2 < items.length) {
        var j = i2;
        while (j + 1 < items.length && items[j + 1].k === items[i2].k) { j++; }
        blocks.push(items.slice(i2, j + 1));
        i2 = j + 1;
      }
      var render = function (b) {
        if (b.length === 1) { return one(b[0]); }
        return '<details class="egroup"><summary>' +
          '<div class="eitem"><span class="ei">' + (I[EI[b[0].k] || 'para']) + '</span>' +
          '<span class="ek">' + esc(b[0].k) + '</span>' +
          '<span class="cntb">' + b.length + '</span>' +
          '<span class="arw">' + I.arrowR + '</span></div></summary>' +
          '<div class="esub">' + b.map(one).join('') + '</div></details>';
      };

      var vis = blocks.slice(0, 4), hid = blocks.slice(4);
      var hidN = hid.reduce(function (n, b) { return n + b.length; }, 0);
      node = el('<details class="edits" open><summary>' +
        '<span class="fwrap"><span class="fi ' + (s.kind || 'w') + '">' +
        KINDCH[s.kind] + '</span>' +
        (s.failed ? '<span class="badge-x"></span>' : '') + '</span>' +
        '<span class="en">' + esc(s.file) + '</span>' +
        '<span class="ec">편집됨 · ' + items.length + '개 편집</span>' +
        '<span class="ar">' + I.caret + '</span></summary>' +
        '<div class="elist">' + vis.map(render).join('') +
        (hid.length ? '<div class="ehid" hidden>' + hid.map(render).join('') + '</div>' +
                      '<button class="emore">+' + hidN + '개 더</button>' : '') +
        '</div></details>');
      var em = node.querySelector('.emore');
      if (em) {
        em.addEventListener('click', function (e) {
          e.preventDefault();
          var h = node.querySelector('.ehid');
          if (h.hasAttribute('hidden')) { h.removeAttribute('hidden'); this.textContent = '간단히 보기'; }
          else { h.setAttribute('hidden', ''); this.textContent = '+' + hidN + '개 더'; }
        });
      }

    } else if (s.t === 'mail') {
      /* 메일 발송 승인 카드. 실제 화면은 보내기 전에 편집 가능한 초안을 띄운다.
         받는 사람은 지울 수 있는 pill, 오른쪽에 참조·숨은 참조 링크가 붙는다. */
      node = el('<div class="mailcard' + (s.disabled ? ' nosend' : '') + '">' +
        '<div class="mhead"><span class="mico">' + I.outlookS + '</span>' +
        '<span class="mtitle">전자 메일을 보내시겠습니까?</span>' +
        '<span class="mdraft">초안 작성</span></div>' +
        '<div class="mrow"><span class="mk">받는 사람:</span>' +
          '<span class="mv">' + (s.to
            ? '<span class="pill-p"><span class="av">' +
              esc((s.to || ' ').trim().charAt(0)) + '</span>' + esc(s.to) +
              '<span class="rmx">' + I.x + '</span></span>'
            : '<span class="mempty"></span>') + '</span>' +
          '<span class="mcc"><button>참조</button><button>숨은 참조</button></span></div>' +
        '<div class="mrow"><span class="mk">제목:</span>' +
          '<span class="mv msub">' + esc(s.subject) + '</span></div>' +
        '<div class="mtb"><button><b>B</b></button><button><i>I</i></button>' +
          '<span class="msep"></span>' +
          '<button>' + I.bullet + '</button><button>' + I.numlist + '</button>' +
          '<span class="msep"></span><button>' + I.clip + '</button></div>' +
        (s.body ? '<div class="mbody">' + rich(s.body) + '</div>' : '') +
        ((s.files || []).length
          ? '<div class="matt">' + s.files.map(function (f) {
              var k = fileKind(f), ext = (f.split('.').pop() || '').toUpperCase();
              return '<span class="attc"><span class="fi ' + k + '">' + KINDCH[k] + '</span>' +
                '<span class="an"><span class="a1">' + esc(f.replace(/\.[^.]+$/, '')) + '</span>' +
                '<span class="a2">' + esc(ext) + '</span></span>' +
                '<span class="rmx">' + I.x + '</span></span>';
            }).join('') + '</div>'
          : '') +
        '<div class="mbtns"><button class="mb">취소</button>' +
        '<button class="mb send">' + I.send + '보내기<span class="cv">' + I.caret + '</span></button></div>' +
        '<div class="mnote"><span class="ni">' + I.info + '</span>' +
        '아래에 메시지를 보내면 편집 내용이 삭제되고 위의 작업이 취소됩니다.</div>' +
        '</div>');

    } else if (s.t === 'prompt') {
      /* 같은 작업에서 이어 시킨 두 번째 프롬프트. 위에 시간 구분선이 붙는다. */
      node = el('<div class="turn"></div>');
      if (s.sep) { node.appendChild(el('<div class="daysep"><span>' + esc(s.sep) + '</span></div>')); }
      node.appendChild(userBubble(s.body, s.time, s.files, false));

    } else if (s.t === 'confirm') {
      /* 도구 실행 승인 카드. 메일 말고도 파일 복사 같은 작업 앞에 이게 뜬다.
         값을 표로 보여주고 사용자가 승인해야 실행된다. */
      node = el('<div class="mailcard confirm">' +
        '<div class="mhead"><span class="mico">' + (I[s.icon] || I.copy) + '</span>' +
        '<span class="mtitle">' + esc(s.title) + '</span></div>' +
        '<div class="krows">' + (s.rows || []).map(function (r) {
          return '<div class="krow"><span class="kk">' + esc(r[0]) + '</span>' +
            '<span class="kv">' + esc(r[1]) + '</span></div>';
        }).join('') + '</div>' +
        '<div class="cfoot"><span class="cnote">' +
        esc(s.note || '승인하기 전에 세부 정보를 검토하세요.') + '</span>' +
        '<span class="mbtns"><button class="mb">취소</button>' +
        '<button class="mb send">' + esc(s.ok || '승인') +
        '<span class="cv">' + I.caret + '</span></button></span></div>' +
        '<div class="mnote"><span class="ni">' + I.info + '</span>' +
        '아래에 메시지를 보내면 편집 내용이 삭제되고 위의 작업이 취소됩니다.</div>' +
        '</div>');

    } else if (s.t === 'cost') {
      /* 대화 도중에 /cost를 찍은 자리. 그 시점의 누적값이 나온다. */
      node = el('<div class="turn"></div>');
      node.appendChild(el('<div class="uwrap"><div class="ubox" style="min-width:0">' +
        '<div class="ubub" style="padding:12px 18px">/cost</div>' +
        '<div class="umeta"><span>' + esc(s.time) + '</span></div>' +
        '</div></div>'));
      node.appendChild(el('<div class="cost"><div class="cic">' + I.clock + '</div><div>' +
        '<div class="l1">이 작업에 크레딧 <b>' + fmt(s.credit) + '</b>개가 사용되었습니다. ' +
        '<span style="font-weight:400;color:var(--ink-3)">(' + usd(s.credit) + ')</span></div>' +
        '<div class="l2">이 시점까지의 누적입니다. 이어서 시키면 값이 올라갑니다.</div>' +
        '</div></div>'));

    } else if (s.t === 'cut') {
      /* 실제 기록이 여기서 끊긴 지점. 이어서 지어내지 않는다. */
      node = el('<div class="cutline"><span>' + esc(s.body) + '</span></div>');

    } else if (s.t === 'approved') {
      /* 사용자가 보내기를 누른 뒤에 남는 줄. */
      node = el('<div class="approved"><div class="apr">' +
        '<span class="ti">' + I.checkThin + '</span>' +
        '<span>' + esc(s.label || '1개 작업 승인됨') + '</span>' +
        '<span class="ar">' + I.arrowR + '</span></div>' +
        (s.sent ? '<div class="tool done"><span class="ti">' + I.mail + '</span>' +
          '<span>' + esc(s.sent) + '</span></div>' : '') +
        (s.done ? '<div class="tool done"><span class="ti">' + I.checkThin + '</span>' +
          '<span>' + esc(s.done) + '</span></div>' : '') + '</div>');

    } else if (s.t === 'ask') {
      /* 진행 도중 되묻기. 질문마다 선택지가 붙고 사용자가 고른 것만 채워진다.
         실제 화면에서는 카드로 뜨고, 답한 뒤에는 고른 값이 사용자 쪽에 남는다. */
      node = el('<div class="askwrap">' +
        (s.body ? '<div class="asay">' + rich(s.body) + '</div>' : '') +
        '<div class="asks">' + (s.items || []).map(function (q, i) {
          return '<div class="askq"><div class="qn">' + (i + 1) + '</div>' +
            '<div class="qb"><div class="qt">' + esc(q.q) + '</div>' +
            '<div class="qo">' + (q.options || []).map(function (o) {
              return '<span class="opt' + (o === q.picked ? ' on' : '') + '">' +
                (o === q.picked ? '<span class="oc">' + I.tickBlue + '</span>' : '') +
                esc(o) + '</span>';
            }).join('') + '</div></div></div>';
        }).join('') + '</div>' +
        '<div class="askmeta">' + esc(s.answerTime || '') + ' · 사용자가 답한 뒤 이어서 진행했습니다</div>' +
        '</div>');

    } else if (s.t === 'agent') {
      var done = s.state === '완료';
      node = el('<div class="agent">' +
        '<span class="sp">' + (done ? I.checkThin : I.spinner) + '</span>' +
        '<span>' + esc(s.name) + '</span>' +
        (done ? '<span class="st">완료</span>' : '') +
        '<span class="ar">' + I.arrowR + '</span></div>');
    }

    if (node) { w.appendChild(node); }

    if (s.t === 'final') {
      /* 여러 턴이 있으면 id가 겹치므로 방금 붙인 노드 안에서 찾는다. */
      var f = node.querySelector('.fin');
      /* 턴마다 그 턴에서 만든 산출물만 붙인다. out이 없으면 전부 붙인다. */
      var pick = s.out || run.artifacts.map(function (_, i) { return i; });
      if (!pick.length) { return; }
      var cards = el('<div class="filecards"></div>');
      pick.forEach(function (i) {
        var a = run.artifacts[i];
        if (!a) { return; }
        var k = fileKind(a.name);
        var c = el('<button class="fcard">' +
          '<span class="fico ' + k + '">' + KINDCH[k] + '</span>' +
          '<span class="ftx"><span class="fn">' + esc(a.name.replace(/\.(docx|pptx|xlsx|html?)$/, '')) + '</span>' +
          '<span class="fk">' + esc(a.kind) + ' · ' + esc(a.meta) + '</span></span>' +
          '<span class="open">' + I.ext + '</span></button>');
        c.addEventListener('click', function () { viewer(i); });
        cards.appendChild(c);
      });
      f.appendChild(cards);
      f.appendChild(el('<div class="react"><button>' + I.copy + '</button>' +
        '<button>' + I.up + '</button><button>' + I.down + '</button>' +
        '<span class="src">소스</span></div>'));
      f.appendChild(el('<div class="outnote">새 응답을 받았습니다. ' +
        '생성된 파일은 세부 정보 창의 출력 폴더에 저장됩니다.</div>'));
    }

    setStatus(s.status || null);
    setPanelAct(s.act || null);
    scroll();
  }

  /* 하단 진행 상태 줄. 실제 화면에서 계속 문구가 바뀐다. */
  function setStatus(text) {
    var old = document.getElementById('statusRow');
    if (old) { old.remove(); }
    if (!text) { return; }
    document.getElementById('w').appendChild(el(
      '<div class="status" id="statusRow"><span class="hex">' + I.hex + '</span>' +
      '<span>' + esc(text) + '</span></div>'));
  }

  /* ── /cost ── */
  function showCost() {
    if (costShown) { return; }
    costShown = true;
    var w = document.getElementById('w');
    setStatus(null);
    w.appendChild(el('<div class="uwrap"><div class="ubox" style="min-width:0">' +
      '<div class="ubub" style="padding:12px 18px">/cost</div>' +
      '<div class="umeta"><span>' +
      esc(run.costTime || run.log[run.log.length - 1].time) + '</span></div>' +
      '</div></div>'));
    w.appendChild(el('<div class="turn" id="costrow"></div>'));
    redrawCost();
    scroll();
  }

  function redrawCost() {
    var row = document.getElementById('costrow');
    if (!row) { return; }
    var pick = picked || run.model;
    var b = run.bench;
    var hit = b.models.filter(function (m) { return m.name === pick; })[0];
    var isReal = pick === run.model;
    var credit = isReal ? run.credit : (hit ? Math.round(hit.avg) : null);
    var unmeasured = !isReal && !hit;
    var max = Math.max.apply(null, b.models.map(function (m) { return m.avg; }));
    var cheapest = b.models.reduce(function (a, m) { return m.avg < a.avg ? m : a; });

    /* 이번 실행의 /cost를 아직 못 받은 시나리오는 크레딧 줄을 감춘다. */
    var head = credit
      ? '<div class="cost"><div class="cic">' + I.clock + '</div><div>' +
        '<div class="l1">이 작업에 크레딧 <b>' + fmt(credit) + '</b>개가 사용되었습니다. ' +
        '<span style="font-weight:400;color:var(--ink-3)">(' + usd(credit) + ')</span></div>' +
        '<div class="l2">' + (isReal
          ? '이 작업에서 실제로 나온 값입니다. <code>/cost</code>는 프롬프트 하나가 아니라 ' +
            '그 작업 전체를 셉니다.'
          : '<b>' + esc(pick) + '</b>로 같은 프롬프트를 돌렸을 때의 실측값입니다.' +
            (hit && hit.effort ? ' 노력 수준은 <b>' + esc(hit.effort) + '</b>이었습니다.' : '')) + '</div>' +
        '</div></div>'
      : '<div class="cost"><div class="cic">' + I.clock + '</div><div>' +
        '<div class="l1">' + (unmeasured
          ? '<b>' + esc(pick) + '</b>로는 이 시나리오를 측정하지 않았습니다.'
          : '이 실행의 크레딧은 아직 확인하지 않았습니다.') + '</div>' +
        '<div class="l2">아래 표는 같은 프롬프트로 실제 측정한 회차입니다. ' +
        '없는 값은 만들지 않습니다.</div>' +
        '</div></div>';

    row.innerHTML =
      '<div>' + head +
        '<div class="bench">' +
          '<h4>' + esc(b.head || '같은 일을 다른 모델로 시키면') + '</h4>' +
          '<div class="lead">' + esc(b.lead ||
            '같은 프롬프트를 모델만 바꿔 돌린 실측값입니다.') + ' 범위는 ' +
            fmt(b.min) + '부터 ' + fmt(b.max) + '까지입니다.</div>' +
          b.models.map(function (m) {
            var on = m.name === pick;
            return '<div class="brow"><div class="bnm' + (on ? ' self' : '') + '">' + esc(m.name) +
              (m.effort ? '<span class="beff">' + esc(m.effort) + '</span>' : '') + '</div>' +
              '<div class="btrack"><div class="bfill' + (on ? ' self' : '') + '" style="width:' +
              Math.max(2, m.avg / max * 100).toFixed(1) + '%"></div></div>' +
              '<div class="bval">' + fmt(Math.round(m.avg)) +
              '<small>' + usd(m.avg) + (m.n > 1 ? ' · ' + m.n + '회' : '') + '</small></div></div>' +
              (m.meta ? '<div class="bmeta">' + esc(m.meta) + '</div>' : '');
          }).join('') +
          '<div class="bnote">' + (credit
            ? (credit === cheapest.avg
                ? '이 회차가 이 중 가장 적게 들었습니다. 가장 많이 든 쪽은 이 회차의 <b>' +
                  (max / credit).toFixed(1) + '배</b>입니다.'
                : '가장 적게 든 <b>' + esc(cheapest.name) + '</b> 대비 <b>' +
                  (credit / cheapest.avg).toFixed(1) + '배</b>입니다.')
            : '가장 적게 든 <b>' + esc(cheapest.name) + '</b>와 가장 많이 든 쪽의 차이는 <b>' +
              (max / cheapest.avg).toFixed(1) + '배</b>입니다.') +
            ' 위 숫자는 이 데모에서 직접 잰 값이고, 상대 비교용입니다. 견적의 근거로 쓰지 않습니다.' +
          '</div>' +
          (b.condition ? '<div class="bcond"><b>측정 조건</b> ' + esc(b.condition) + '</div>' : '') +
        '</div>' +
      '</div>';
  }

  /* ── 재생 제어 ── */
  function tick() {
    var total = run.log.length + 1;
    var cur = Math.min(idx + (costShown ? 1 : 0), total);
    document.getElementById('cnt').textContent = cur + '/' + total;
    document.getElementById('bar').style.width = (cur / total * 100) + '%';
    syncPanel();
  }
  function step() {
    if (idx < run.log.length) { emit(run.log[idx]); idx++; tick(); return; }
    if (!costShown) { showCost(); tick(); return; }
    stop();
  }
  function start() {
    clearInterval(timer);
    timer = setInterval(step, 1600 / speed);
    document.getElementById('play').innerHTML = I.pause + '<span>일시정지</span>';
    document.getElementById('play').addEventListener('click', toggle, { once: true });
    setRunningUI(true);
  }
  function stop() {
    clearInterval(timer); timer = null;
    var p = document.getElementById('play');
    if (p) {
      p.innerHTML = I.play + '<span>재생</span>';
      p.addEventListener('click', toggle, { once: true });
    }
    setRunningUI(false);
    if (costShown) { setStatus(null); }
  }
  function toggle() { timer ? stop() : start(); }
  function skipAll() {
    stop();
    while (idx < run.log.length) { emit(run.log[idx]); idx++; }
    setStatus(null);
    showCost(); tick();
  }

  /* ── 뷰어 ── */
  function viewer(i) {
    var a = run.artifacts[i], v = document.getElementById('viewer');
    v.querySelector('.vn').textContent = a.name;
    v.querySelector('.vm').textContent = a.kind + ' · ' + a.meta;
    v.querySelector('.vbody').innerHTML = (a.pages || []).length
      ? a.pages.map(function (p) { return '<img src="' + p + '" alt="" loading="lazy">'; }).join('')
      : '<div class="vnone">' +
        (a.kind.indexOf('메일') > -1
          ? '메일 초안은 파일이 아니라 임시보관함에 남아 있습니다. 대화에서 초안 카드를 확인하세요.'
          : '이 산출물은 미리보기를 만들어 두지 않았습니다.') +
        (a.file ? '<a href="' + a.file + '" target="_blank" rel="noopener">파일 열기</a>' : '') +
        '</div>';
    v.classList.add('on');
  }

  /* ── 초기화 ── */
  document.addEventListener('click', function () { closePops(); });
  document.getElementById('viewer').addEventListener('click', function (e) {
    if (e.target.id === 'viewer' || e.target.closest('.vx')) { this.classList.remove('on'); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closePops();
      document.getElementById('viewer').classList.remove('on');
    }
    if (e.key === ' ' && run && ['INPUT', 'SELECT', 'TEXTAREA'].indexOf(e.target.tagName) < 0) {
      e.preventDefault(); toggle();
    }
  });

  buildSide();
  renderHome();
})();


