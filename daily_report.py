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
        print("skip: " + str(e))
        return None

print("Fetching market data...")

# 1. 大盘
idx = ec(ak.stock_zh_index_daily, symbol="sh000001")
if idx is not None:
    last = idx.iloc[-1]
    sh_c = last['close']
    sh_pct = (sh_c - last['open']) / last['open'] * 100
else:
    sh_c, sh_pct = '--', 0

# 2. 全市场
sp = ec(ak.stock_zh_a_spot_em)
up = down = 0
limit_list = []
if sp is not None:
    cols = sp.columns.tolist()
    print("columns: " + str(cols))
    up = int((sp.iloc[:, 3].astype(float) > 0).sum())
    down = int((sp.iloc[:, 3].astype(float) < 0).sum())
    limit10 = sp[sp.iloc[:, 3].astype(float) >= 9.8].head(10)

# 3. 涨停
zt = ec(ak.stock_zt_pool_em, date="20260701")
zt_count = 0
zt_top = pd.DataFrame()
if zt is not None:
    zt_count = len(zt)
    zt_top = zt.head(10)

# 4. 板块
bd = ec(ak.stock_board_industry_name_em)
top_sec = pd.DataFrame()
if bd is not None:
    cols = bd.columns.tolist()
    print("board cols: " + str(cols))
    top_sec = bd.sort_values(by=bd.columns[3], ascending=False).head(5)

# 5. 北向
nf = ec(ak.stock_hsgt_north_net_flow_in_em, symbol="沪股通")
n_val = '--'
if nf is not None and len(nf) > 0:
    n_val = nf['value'].iloc[-1]

# 6. 融资
rz = ec(ak.stock_margin_sz_sh_szse, start_date="20260701")
rz_str = '--'
if rz is not None and len(rz) > 0:
    rz_str = str(rz.iloc[-1].get('融资余额', rz.iloc[-1][0]))

# 7. 龙虎榜
lh = ec(ak.stock_lhb_jgmm_tj_em)
lh_top = pd.DataFrame()
if lh is not None:
    lh_top = lh.head(5)

# 8. 行业资金
fund = ec(ak.stock_sector_fund_flow_rank, indicator="今日", sector_type="行业资金流向")
fund_top = pd.DataFrame()
if fund is not None:
    fund_top = fund.head(5)

# 生成报告
lines = []
lines.append("A股盘前分析")
lines.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
lines.append("")

lines.append("[大盘]")
lines.append("上证: {} ({:+.2f}%)".format(sh_c, sh_pct))
lines.append("涨:{} 跌:{}".format(up, down))
lines.append("涨停:{}只".format(zt_count))
lines.append("")

if n_val != '--':
    lines.append("[北向]")
    lines.append("沪股通: {:.0f}亿".format(n_val))
    lines.append("")

lines.append("[融资余额]")
lines.append(str(rz_str))
lines.append("")

if len(top_sec) > 0:
    lines.append("[强势板块]")
    for _, r in top_sec.iterrows():
        lines.append("  {}: {:+.2f}%".format(r.iloc[1], r.iloc[3]))
    lines.append("")

if len(fund_top) > 0:
    lines.append("[资金流入]")
    for _, r in fund_top.iterrows():
        lines.append("  {}: {}".format(r.iloc[0], r.iloc[2]))
    lines.append("")

if zt_count > 0:
    lines.append("[涨停聚焦]")
    for _, r in zt_top.iterrows():
        lines.append("  {}: {:.1f}%".format(r.iloc[1], r.iloc[3]))
    lines.append("")

if len(lh_top) > 0:
    lines.append("[龙虎榜]")
    for _, r in lh_top.iterrows():
        lines.append("  {} {}: {}亿".format(
            r.iloc[0], r.iloc[1],
            round(float(r.iloc[3])/1e8, 2) if '亿' not in str(r.iloc[3]) else r.iloc[3]))
    lines.append("")

content = '\n'.join(lines)
print("=== REPORT ===")
print(content)

t = os.environ.get('PUSHPLUS_TOKEN', os.environ.get('TOKEN', ''))
if t:
    d = {'token': t, 'title': 'A股盘前', 'content': content, 'template': 'txt'}
    r = urllib.request.Request('http://www.pushplus.plus/send',
        data=json.dumps(d).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(r, timeout=15)
        result = json.loads(resp.read())
        if result.get('code') == 200:
            print("PUSH OK")
        else:
            print("PUSH fail: " + str(result))
    except Exception as e:
        print("PUSH error: " + str(e))
