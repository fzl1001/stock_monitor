# -*- coding: utf-8 -*-
"""A鑲＄洏鍓嶅垎鏋?- 鍩轰簬akshare鐨勫鏁版嵁婧愮患鍚堣剼鏈?""
import json, os, sys, urllib.request, base64, datetime

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

# ============ 1. 澶х洏琛屾儏 ============
print("1/10 澶х洏鎸囨暟...")
try:
    df = ak.stock_zh_index_daily(symbol="sh000001")
    sh_latest = df.iloc[-1]
    sh_close = sh_latest['close']
    sh_pct = (sh_close - sh_latest['open']) / sh_latest['open'] * 100
except:
    sh_close, sh_pct = '--', '--'

# ============ 2. 鍏ㄥ競鍦烘定璺屽垎甯?============
print("2/10 娑ㄨ穼瀹舵暟...")
try:
    df = ak.stock_zh_a_spot_em()
    up = len(df[df['娑ㄨ穼骞?] > 0])
    down = len(df[df['娑ㄨ穼骞?] < 0])
    limit_up = df[df['娑ㄨ穼骞?] >= 9.8].head(15)
except:
    up, down, limit_up = 0, 0, pd.DataFrame()

# ============ 3. 娑ㄥ仠鏉?============
print("3/10 娑ㄥ仠鏁版嵁...")
try:
    df_zt = ak.stock_zt_pool_em(date="20260701")
    zt_count = len(df_zt)
    zt_top = df_zt.head(10)
except:
    zt_count, zt_top = 0, pd.DataFrame()

# ============ 4. 鏉垮潡鎺掑悕 ============
print("4/10 鏉垮潡鎺掕...")
try:
    df_hangye = ak.stock_board_industry_name_em()
    top_sectors = df_hangye.sort_values('娑ㄨ穼骞?, ascending=False).head(5)
except:
    top_sectors = pd.DataFrame()

# ============ 5. 鍖楀悜璧勯噾 ============
print("5/10 鍖楀悜璧勯噾...")
try:
    df_north = ak.stock_hsgt_north_net_flow_in_em(symbol="娌偂閫?)
    north_val = df_north['value'].iloc[-1] if len(df_north) > 0 else '--'
except:
    north_val = '--'

# ============ 6. 鍏ㄧ悆鎸囨暟 ============
print("6/10 鍏ㄧ悆鎸囨暟...")
try:
    df_global = ak.stock_us_spot_em()
    sp500 = df_global[df_global['鍚嶇О'].str.contains('鏍囨櫘|S&P|SPX', case=False)].head(1)
except:
    sp500 = pd.DataFrame()

# ============ 7. 鍟嗗搧鏈熻揣 ============
print("7/10 鍟嗗搧鏈熻揣...")
try:
    gold = safe_call(ak.futures_foreign_hist, {}, symbol="榛勯噾")
    oil = safe_call(ak.futures_foreign_hist, {}, symbol="鍘熸补")
except:
    gold, oil = {}, {}

# ============ 8. 榫欒檸姒?============
print("8/10 榫欒檸姒?..")
try:
    df_lh = ak.stock_lhb_jgmm_tj_em()
    lh_top = df_lh.head(5) if len(df_lh) > 0 else pd.DataFrame()
except:
    lh_top = pd.DataFrame()

# ============ 9. 铻嶈祫铻嶅埜 ============
print("9/10 涓よ瀺鏁版嵁...")
try:
    df_rz = ak.stock_margin_sz_sh_szse(start_date="20260701")
    rz_val = df_rz['铻嶈祫浣欓'].iloc[-1] if len(df_rz) > 0 else '--'
except:
    rz_val = '--'

# ============ 10. 琛屼笟璧勯噾娴佸悜 ============
print("10/10 琛屼笟璧勯噾...")
try:
    df_fund = ak.stock_sector_fund_flow_rank(indicator="浠婃棩", sector_type="琛屼笟璧勯噾娴佸悜")
    top_fund = df_fund.head(5) if len(df_fund) > 0 else pd.DataFrame()
except:
    top_fund = pd.DataFrame()

# ============ 鐢熸垚鎶ュ憡 ============
token = os.environ.get('PUSHPLUS_TOKEN', os.environ.get('TOKEN', ''))
if not token:
    token = "a47cdc0712a9436a8e8f978b5847ca71"
    print(f"Using default token (no secret)")

lines = []
lines.append("A鑲＄洏鍓嶅垎鏋愭姤鍛?)
lines.append(f"鏃堕棿: {datetime.datetime.now().strftime('%H:%M')}")
lines.append("")

lines.append("銆愬ぇ鐩樻寚鏁般€?)
lines.append(f"涓婅瘉: {sh_close} ({sh_pct:+.2f}%)")
lines.append(f"娑ㄨ穼姣? {up}娑?/ {down}璺?)
lines.append(f"娑ㄥ仠: {zt_count}鍙?)
lines.append("")

lines.append("銆愬寳鍚戣祫閲戙€?)
lines.append(f"娌偂閫? {north_val}浜? if isinstance(north_val, str) else f"娌偂閫? {north_val:.0f}浜?)
lines.append("")

lines.append("銆愬己鍔挎澘鍧椼€?)
if len(top_sectors) > 0:
    for _, r in top_sectors.iterrows():
        lines.append(f"  {r['鏉垮潡鍚嶇О']}: {r['娑ㄨ穼骞?]:+.2f}%")
lines.append("")

lines.append("銆愯涓氳祫閲戞祦鍏ャ€?)
if len(top_fund) > 0:
    for _, r in top_fund.iterrows():
        lines.append(f"  {r['琛屼笟']}: {r['涓诲姏鍑€娴佸叆-鍑€棰?]}")
lines.append("")

lines.append("銆愭定鍋滆仛鐒︺€?)
if zt_count > 0:
    for _, r in zt_top.iterrows():
        lines.append(f"  {r['浠ｇ爜']} {r['鍚嶇О']}: {r['娑ㄨ穼骞?]}% ({r.get('娑ㄥ仠缁熻','')[:8]})")
lines.append("")

lines.append("銆愯瀺璧勮瀺鍒搞€?)
lines.append(f"浣欓: {rz_val}")
lines.append("")

lines.append("銆愰緳铏庢鍏虫敞銆?)
if len(lh_top) > 0:
    for _, r in lh_top.iterrows():
        lines.append(f"  {r.get('鑲＄エ浠ｇ爜','')} {r.get('鑲＄エ鍚嶇О','')}: {r.get('鎴愪氦棰?,'')}")
lines.append("")

lines.append("銆愭槑鏃ュ叧娉ㄦ柟鍚戙€?)
lines.append("寰呰ˉ鍏?)
lines.append("")
lines.append("鏁版嵁婧? akshare(涓滄柟璐㈠瘜/鍚岃姳椤?")

content = '\n'.join(lines)
print(content)

if token:
    push_data = {
        'token': token,
        'title': f'A鑲＄洏鍓嶆姤鍛?{datetime.date.today()}',
        'content': content,
        'template': 'txt'
    }
    req = urllib.request.Request(
        'http://www.pushplus.plus/send',
        data=json.dumps(push_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        print(f'\n鎺ㄩ€? {"鎴愬姛" if result.get("code")==200 else "澶辫触"}')
    except Exception as e:
        print(f'\n鎺ㄩ€佸け璐? {e}')
else:
    print('\n鏈厤缃甌oken锛岃烦杩囨帹閫?)
