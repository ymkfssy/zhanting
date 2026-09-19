import urllib.request as u, urllib.error, os
paths = ['/', '/index.html', '/admin.html', '/api/config', '/assets/css/style.css']
lines = []
for p in paths:
    try:
        r = u.urlopen('http://localhost:8123' + p, timeout=5)
        lines.append('%s -> %d' % (p, r.status))
    except Exception as e:
        lines.append('%s -> ERR %s' % (p, e))
with open(r'C:\Users\gaolin\WorkBuddy\展厅控制\check_up.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('CHECKED')
