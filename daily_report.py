import json, os, sys, urllib.request, datetime

try:
    import akshare as ak
except ImportError:
    os.system("pip install akshare pandas --quiet 2>/dev/null")
    import akshare as ak

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

def safe_call(fn, default=None, *a, **kw):
    try: return fn(*a, **kw)
    except Exception as e:
        if default is not None: return default
        return {}

print("1/10 澶х洏琛屾儏...")
try:
    df = ak.stock_zh_index_daily(symbol="sh000001")
    sh_close = df.iloc[-1]['close']
    sh_open = df.iloc[-1]['open']
    sh_pct = (sh_close - sh_open) / sh_open * 100
except Exception as e:
    sh_close, sh_pct = '--', 0
    print(f"  skip: {e}")

print("2/10 娑ㄨ穼鍒嗗竷...")
try:
    df = ak.stock_zh_a_spot_em()
    up = int((df['娑ㄨ穼骞?] > 0).sum())
    down = int((df['娑ㄨ穼骞?] < 0).sum())
    limit_up_df = df[df['娑ㄨ穼骞?] >= 9.8].head(15)
except Exception as e:
    up, down, limit_up_df = 0, 0, pd.DataFrame()
    print(f"  skip: {e}")

print("3/10 娑ㄥ仠鏉?..")
try:
    df_zt = ak.stock_zt_pool_em(date="20260701")
    zt_count = len(df_zt)
    zt_top = df_zt.head(10)
except Exception as e:
    zt_count, zt_top = 0, pd.DataFrame()
    print(f"  skip: {e}")

print("4/10 鏉垮潡鎺掕...")
try:
    df_board = ak.stock_board_industry_name_em()
    top_sectors = df_board.sort_values('娑ㄨ穼骞?, ascending=False).head(5)
except Exception as e:
    top_sectors = pd.DataFrame()
    print(f"  skip: {e}")

print("5/10 鍖楀悜璧勯噾...")
try:
    df_north = ak.stock_hsgt_north_net_flow_in_em(symbol="娌偂閫?)
    north_val = df_north['value'].iloc[-1]
except Exception as e:
    north_val = '--'
    print(f"  skip: {e}")

print("6/10 铻嶈祫铻嶅埜...")
try:
    df_rz = ak.stock_margin_sz_sh_szse(start_date="20260701")
    rz_val = df_rz.iloc[-1]
except Exception as e:
    rz_val = None
    print(f"  skip: {e}")

print("7/10 鍏ㄧ悆鎸囨暟...")
try:
    df_us = ak.stock_us_spot_em()
except Exception as e:
    df_us = pd.DataFrame()
    print(f"  skip: {e}")

print("8/10 榫欒檸姒?..")
try:
    df_lh = ak.stock_lhb_jgmm_tj_em()
    lh_top = df_lh.head(5)
except Exception as e:
    lh_top = pd.DataFrame()
    print(f"  skip: {e}")

print("9/10 琛屼笟璧勯噾...")
try:
    df_fund = ak.stock_sector_fund_flow_rank(indicator="浠婃棩", sector_type="琛屼笟璧勯噾娴佸悜")
    top_fund = df_fund.head(5)
except Exception as e:
    top_fund = pd.DataFrame()
    print(f"  skip: {e}")

print("10/10 鐢熸垚鎶ュ憡...")

lines = []
lines.append("A鑲＄洏鍓嶅垎鏋愭姤鍛?)
lines.append("鏃堕棿: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
lines.append("")
lines.append("銆愬ぇ鐩樻寚鏁般€?)
lines.append("涓婅瘉: {} ({:+.2f}%)".format(sh_close, sh_pct))
lines.append("")
lines.append("銆愭定璺屽垎甯冦€?)
lines.append("涓婃定: {} 涓嬭穼: {}".format(up, down))
lines.append("娑ㄥ仠: {}鍙?.format(zt_count))
lines.append("")
if north_val != '--':
    lines.append("銆愬寳鍚戣祫閲戙€?)
    lines.append("娌偂閫? {:.0f}浜?.format(north_val))
    lines.append("")
if rz_val is not None:
    lines.append("銆愯瀺璧勮瀺鍒搞€?)
    lines.append("铻嶈祫浣欓: " + str(rz_val.get('铻嶈祫浣欓', '--')))
    lines.append("")
if len(top_sectors) > 0:
    lines.append("銆愬己鍔挎澘鍧椼€?)
    for _, r in top_sectors.iterrows():
        lines.append("  {}: {:+.2f}%".format(r['鏉垮潡鍚嶇О'], r['娑ㄨ穼骞?]))
    lines.append("")
if len(top_fund) > 0:
    lines.append("銆愯祫閲戞祦鍏ヨ涓氥€?)
    for _, r in top_fund.iterrows():
        lines.append("  {}: {}".format(r['琛屼笟'], r['涓诲姏鍑€娴佸叆-鍑€棰?]))
    lines.append("")
if zt_count > 0:
    lines.append("銆愭定鍋滆仛鐒︺€?)
    for _, r in zt_top.iterrows():
        lines.append("  {} {}: {:.1f}%".format(r['浠ｇ爜'], r['鍚嶇О'], r['娑ㄨ穼骞?]))
    lines.append("")
if len(lh_top) > 0:
    lines.append("銆愰緳铏庢鍏虫敞銆?)
    for _, r in lh_top.iterrows():
        lines.append("  {} {}: {}浜?.format(r.get('鑲＄エ浠ｇ爜',''), r.get('鑲＄エ鍚嶇О',''), round(r.get('鎴愪氦棰?,0)/1e8, 2)))
    lines.append("")

content = '\n'.join(lines)
print(content)

token = os.environ.get('PUSHPLUS_TOKEN', os.environ.get('TOKEN', ''))
if token:
    push_data = {'token': token, 'title': 'A鑲＄洏鍓嶅垎鏋?, 'content': content, 'template': 'txt'}
    req = urllib.request.Request(
        'http://www.pushplus.plus/send',
        data=json.dumps(push_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        r = json.loads(resp.read())
        print("鎺ㄩ€? " + ("鎴愬姛" if r.get('code')==200 else "澶辫触"))
    except Exception as e:
        print("鎺ㄩ€佸け璐? " + str(e))
