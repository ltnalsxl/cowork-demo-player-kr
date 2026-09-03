# -*- coding: utf-8 -*-
"""모든 시나리오를 한 번에 다시 굽는다.

크레딧을 재지 않은 회차는 _보류/로 옮겨 두었다. /cost를 받으면 되살린다.
"""
import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
for s in ['build_sonnet.py', 'build_terra.py',
          'build_badge.py', 'build_isms.py', 'build_brief.py', 'build_skill.py',
          'build_weekly.py', 'build_inbox.py',
          'group.py', 'fetch_fx.py', 'build.py']:
    r = subprocess.run([sys.executable, os.path.join(BASE, s)], cwd=BASE)
    if r.returncode:
        sys.exit(r.returncode)




