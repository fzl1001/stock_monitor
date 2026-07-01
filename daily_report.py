import json, os, sys, urllib.request, datetime

try:
    import akshare as ak
except ImportError:
    os.system("pip install akshare pandas --quiet 2>/dev/null")
    import akshare as ak

import pandas as pd

def ec(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception as e:
        print("skip: " + str(e)[:120])
        return None

print("1. 大盘...")
idx = ec(ak.stock_zh_index_daily, symbol="sh000001")
if idx is not None:
    last = idx.iloc[-1]
    sh_c = last.iloc[3]
    sh_pct = (sh_c - last.iloc[1]) / last.iloc[1] * 100
    print("  sh: " + str(round(sh_c,2)) + " (" + str(round(sh_pct,2)) + "%)")
else:
    sh_c, sh_pct = '--', 0

print("2. 全市场...")
sp = ec(ak.stock_zh_a_spot_em)
up = down = 0
if sp is not None:
    pcol = sp.columns[3]
    up = int((sp[pcol].astype(float) > 0).sum())
    down = int((sp[pcol].astype(float) < 0).sum())
    limit10 = sp[sp[pcol].astype(float) >= 9.8].head(10)
    print("  涨:{} 跌:{}".format(up, down))

print("3. 涨停...")
zt = ec(ak.stock_zt_pool_em, date="20260701")
zt_count = 0
if zt is not None:
    zt_count = len(zt)
    zt_top = zt.head(10)
    print("  涨停: " + str(zt_count))

print("4. 板块...")
bd = ec(ak.stock_board_industry_name_em)
if bd is not None:
    pcol = bd.columns[3]
    top_sec = bd.sort_values(by=pcol, ascending=False).head(5)
    print("  top: " + str(top_sec.iloc[0,1]))

print("5. 北向...")
try:
    nf = ak.stock_hsgt_north_net_flow_in_em(symbol="沪股通")
except:
    nf = None
if nf is not None and len(nf) > 0:
    n_val = nf['value'].iloc[-1]
    print("  北向: " + str(round(n_val, 0)))
else:
    n_val = '--'

print("6. 两融...")
rz = ec(ak.stock_margin_sz_sh_szse, start_date="20260701")
rz_str = '--'
if rz is not None and len(rz) > 0:
    rz_str = str(rz.iloc[-1, 0])

print("7. 龙虎榜...")
lh = ec(ak.stock_lhb_jgmm_tj_em)
if lh is not None:
    lh_top = lh.head(5)

print("8. 资金...")
fund = ec(ak.stock_sector_fund_flow_rank, indicator="今日", sector_type="行业资金流向")
if fund is not None:
    fund_top = fund.head(5)

print("9. 生成报告...")
lines = []
lines.append("A股盘前分析")
lines.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
lines.append("")
lines.append("【大盘】")
if isinstance(sh_c, str):
    lines.append("上证: " + sh_c)
else:
    lines.append("上证: " + "{:.2f} ({:+.2f}%)".format(sh_c, sh_pct))
lines.append("涨跌: {} / {}".format(up, down))
lines.append("涨停: {}只".format(zt_count))
lines.append("")
if n_val != '--':
    lines.append("【北向】")
    lines.append("沪股通: {:.0f}亿".format(n_val))
    lines.append("")
if rz_str != '--':
    lines.append("【两融】")
    lines.append("余额: " + rz_str)
    lines.append("")
if bd is not None:
    lines.append("【强势板块】")
    for _, r in top_sec.iterrows():
        lines.append("  {}: {:+.2f}%".format(r.iloc[1], r.iloc[3]))
    lines.append("")
if fund is not None:
    lines.append("【资金流入】")
    for _, r in fund_top.iterrows():
        lines.append("  {}: {}".format(r.iloc[0], r.iloc[2]))
    lines.append("")
if zt_count > 0:
    lines.append("【涨停聚焦】")
    for _, r in zt_top.iterrows():
        lines.append("  {}: {:.1f}%".format(r.iloc[1], r.iloc[3]))
    lines.append("")
if lh is not None:
    lines.append("【龙虎榜】")
    lh_cols = lh.columns.tolist()
    for _, r in lh_top.iterrows():
        code = r.iloc[0]
        name = r.iloc[1]
        amount = r.iloc[3]
        try:
            amt = round(float(amount)/1e8, 2)
        except:
            amt = amount
        lines.append("  {} {}: {}亿".format(code, name, amt))
    lines.append("")

content = '\n'.join(lines)
print("=== REPORT START ===")
print(content)
print("=== REPORT END ===")

# Use WX_PUSH_KEY as env var
t = os.environ.get('WX_PUSH_KEY', '')
if not t:
    t = os.environ.get('TOKEN', '')

if t:
    d = {'token': t, 'title': 'A股盘前分析', 'content': content, 'template': 'txt'}
    r = urllib.request.Request('http://www.pushplus.plus/send',
        data=json.dumps(d).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(r, timeout=15)
        result = json.loads(resp.read())
        if result.get('code') == 200:
            print("=> PUSH OK, check your WeChat")
        else:
            print("=> PUSH fail: " + str(result))
    except Exception as e:
        print("=> PUSH error: " + str(e))
else:
    print("=> NO TOKEN, skip push")
