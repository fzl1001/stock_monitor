import json, urllib.request, sys, os

token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('TOKEN', '')
title = sys.argv[2] if len(sys.argv) > 2 else 'A鑲℃姤鍛?
time_str = sys.argv[3] if len(sys.argv) > 3 else ''

if not token:
    print('No token provided')
    sys.exit(1)

# Read content from stdin if available
content = sys.stdin.read() if not sys.stdin.isatty() else f'鎶ュ憡鏃堕棿: {time_str}'

push_data = {
    'token': token,
    'title': title,
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
    if result.get('code') == 200:
        print(f'鎺ㄩ€佹垚鍔? {title}')
    else:
        print(f'鎺ㄩ€佸紓甯? {result}')
except Exception as e:
    print(f'鎺ㄩ€佸け璐? {e}')
