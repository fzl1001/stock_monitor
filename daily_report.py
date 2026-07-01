import json, os, sys, urllib.request, datetime

try:
    import akshare as ak
except ImportError:
    os.system("pip install akshare pandas --quiet 2>/dev/null")
    import akshare as ak

import pandas as pd

def ec(fn, *a, **kw):
    try: return fn(*a, **kw)
    except Exception as e:
        print("skip: " + str(e)[:100])
        return None

print("1. index")
idx = ec(ak.stock_zh_index_daily, symbol="sh000001")
if idx is not None:
    last = idx.iloc[-1]
    sh_c = last.iloc[3]
    sh_pct = (sh_c - last.iloc[1]) / last.iloc[1] * 100
else:
    sh_c, sh_pct = '--', 0

print("2. spots (retry up to 3 times)")
sp = None
for i in range(3):
    sp = ec(ak.stock_zh_a_spot_em)
    if sp is not None: break
    import time; time.sleep(3)

up = down = 0
if sp is not None:
    pcol = sp.columns[3]
    up = int((sp[pcol].astype(float) > 0).sum())
    down = int((sp[pcol].astype(float) < 0).sum())
else:
    print("  all spot attempts failed")

print("3. zhangting")
zt = ec(ak.stock_zt_pool_em, date="20260701")
zt_count = 0 if zt is None else len(zt)

print("4. hangye")
bd = ec(ak.stock_board_industry_name_em)

print("5. beixiang")
try:
    nf = ec(ak.stock_hsgt_north_net_flow_in_em, symbol="沪股通")
except:
    nf = None
n_val = '--'

# Build report
lines = []
lines.append("A股盘前分析")
lines.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
lines.append("")
if isinstance(sh_c, str):
    lines.append("上证: " + sh_c)
else:
    lines.append("上证: {:.2f} ({:+.2f}%)".format(sh_c, sh_pct))
lines.append("涨:{} 跌:{}".format(up, down))
lines.append("涨停: {}只".format(zt_count))
lines.append("")
if bd is not None:
    try:
        pcol = bd.columns[3]
        ts = bd.sort_values(by=pcol, ascending=False).head(5)
        lines.append("强势板块")
        for _, r in ts.iterrows():
            lines.append("  {}: {:+.1f}%".format(r.iloc[1], r.iloc[3]))
        lines.append("")
    except: pass
if zt is not None:
    lines.append("涨停聚焦")
    for _, r in zt.head(10).iterrows():
        lines.append("  {}: {:.1f}%".format(r.iloc[1], r.iloc[3]))
    lines.append("")

content = '\n'.join(lines)
print("=== REPORT ===")
print(content)

t = os.environ.get('WX_PUSH_KEY', '')
print("\nToken from env: " + ("set (" + str(len(t)) + " chars)" if t else "EMPTY!"))

# Fallback: hardcode token directly (as last resort)
if not t:
    t = "a47cdc0712a9436a8e8f978b5847ca71"
    print("Using hardcoded token")

d = {'token': t, 'title': 'A股盘前测试', 'content': content, 'template': 'txt'}
r = urllib.request.Request('http://www.pushplus.plus/send',
    data=json.dumps(d).encode('utf-8'),
    headers={'Content-Type': 'application/json'}, method='POST')
try:
    resp = urllib.request.urlopen(r, timeout=15)
    result = json.loads(resp.read())
    if result.get('code') == 200:
        print("=> PUSH SUCCESS, check WeChat!")
    else:
        print("=> PUSH fail: " + str(result))
except Exception as e:
    print("=> PUSH error: " + str(e))
