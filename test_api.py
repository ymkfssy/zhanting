import json
import urllib.request

BASE = "http://localhost:8200"


def get():
    with urllib.request.urlopen(BASE + "/api/config", timeout=5) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def post(obj):
    data = json.dumps(obj).encode("utf-8")
    req = urllib.request.Request(
        BASE + "/api/config", data=data, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


print("=== GET 初始 ===")
try:
    s, c = get()
    print("status", s)
    print(json.dumps(c, ensure_ascii=False, indent=2))
except Exception as e:
    print("GET 失败:", repr(e))
    raise SystemExit

print("\n=== POST 修改 ===")
new = {
    "title": "移动展厅控制中心",
    "screens": [
        {"id": "s_a", "name": "欢迎页", "url": "https://example.com/welcome", "icon": "🏠", "enabled": True},
        {"id": "s_b", "name": "新增大屏", "url": "https://example.com/new", "icon": "🆕", "enabled": True},
    ],
}
s, c = post(new)
print("status", s)
print(json.dumps(c, ensure_ascii=False, indent=2))

print("\n=== GET 再次（确认持久化）===")
s, c = get()
print("status", s, "title=", c.get("title"), "screens=", len(c.get("screens", [])))

print("\n=== 静态页检测 ===")
for path in ("/", "/admin.html", "/assets/js/store.js"):
    try:
        with urllib.request.urlopen(BASE + path, timeout=5) as r:
            print(path, "->", r.status)
    except Exception as e:
        print(path, "失败:", repr(e))
