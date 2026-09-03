# -*- coding: utf-8 -*-
"""달러/원 환율을 받아 data/fx.js로 굽는다.

크레딧 옆에 원화를 함께 보여주려면 환율이 필요하다. 정적 사이트라
브라우저에서 매번 부르지 않고 빌드 때 심는다. 갱신은 GitHub Actions가 맡는다.

받아오지 못하면 있던 값을 그대로 두고 끝낸다. 환율 하나 때문에 빌드가
멈추면 안 되고, 임의로 지어낸 숫자를 싣지도 않는다.
"""
import io
import json
import os
import sys
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, '..', 'data', 'fx.js')

# 앞의 것이 실패하면 다음으로 넘어간다.
SOURCES = [
    ('frankfurter',
     'https://api.frankfurter.dev/v1/latest?base=USD&symbols=KRW',
     lambda d: (d['rates']['KRW'], d['date'])),
    ('open.er-api',
     'https://open.er-api.com/v6/latest/USD',
     lambda d: (d['rates']['KRW'], d.get('time_last_update_utc', '')[:16])),
    ('currency-api',
     'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.min.json',
     lambda d: (d['usd']['krw'], d.get('date', ''))),
]


def fetch():
    for name, url, pick in SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'cowork-demo/1.0'})
            with urllib.request.urlopen(req, timeout=12) as r:
                rate, date = pick(json.loads(r.read().decode('utf-8')))
            rate = float(rate)
            # 한 자릿수나 수만 원이 나오면 응답이 뒤집힌 것이다. 그런 값은 싣지 않는다.
            if not (500 < rate < 3000):
                print('  %s: 값이 범위를 벗어남 (%s)' % (name, rate))
                continue
            return {'usdkrw': round(rate, 2), 'date': date, 'src': name}
        except Exception as e:
            print('  %s: %s' % (name, e))
    return None


def main():
    fx = fetch()
    if not fx:
        if os.path.exists(OUT):
            print('환율을 받지 못해 있던 값을 그대로 둡니다.')
            print(io.open(OUT, encoding='utf-8').read().strip().splitlines()[-1])
            return
        print('환율을 받지 못했고 기존 값도 없습니다. 원화 표기는 생략됩니다.')
        io.open(OUT, 'w', encoding='utf-8').write(
            '/* 자동 생성 파일. _작업/fetch_fx.py 로 다시 만든다. */\n'
            'window.COWORK_FX = null;\n')
        return

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('/* 자동 생성 파일. _작업/fetch_fx.py 로 다시 만든다. */\n')
        fh.write('window.COWORK_FX = ')
        json.dump(fx, fh, ensure_ascii=False)
        fh.write(';\n')
    print('USD/KRW %s (%s, %s)' % (fx['usdkrw'], fx['date'], fx['src']))


if __name__ == '__main__':
    main()
