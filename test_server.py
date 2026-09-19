import json, urllib.request, urllib.error, os, time

PORT = 8300
BASE = "http://localhost:%d" % PORT
OUT = r"C:\Users\gaolin\WorkBuddy\展厅控制\test_server_result.txt"

def req(method, path, body=None):
    url = BASE + path
    data = None
    headers = {}
    if body is not None:
        data = body.encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")

lines = []
def log(s):
    lines.append(str(s))

# 0) 确保没有旧 data.json 干扰
df = r"C:\Users\gaolin\WorkBuddy\展厅控制\data.json"
if os.path.exists(df):
    os.remove(df)
    log("已删除旧 data.json")

# 1) GET 初始：应自动生成默认 4 屏
s, b = req("GET", "/api/config")
log("1) GET /api/config 初始 -> %s" % s)
cfg = json.loads(b)
log("   默认屏数=%d, title=%s" % (len(cfg["screens"]), cfg["title"]))
log("   默认屏名=%s" % "、".join(x["name"] for x in cfg["screens"]))

# 2) 模拟 17 屏写入（含中文、含 enabled=false 隐藏项）
screens = [{"id": "s%d" % i, "name": "屏幕%d号" % (i + 1),
            "url": "https://example.com/%d" % i, "icon": "📺", "enabled": i != 16}
           for i in range(17)]
payload = json.dumps({"title": "大同移动展厅", "screens": screens}, ensure_ascii=False)
s, b = req("POST", "/api/config", payload)
log("2) POST /api/config 17屏 -> %s" % s)
resp = json.loads(b)
log("   返回屏数=%d, 可见(enabled)屏数=%d" % (len(resp["screens"]), sum(1 for x in resp["screens"] if x["enabled"])))

# 3) 再次 GET 确认持久化
s, b = req("GET", "/api/config")
cfg = json.loads(b)
log("3) GET 确认持久化 -> %s, 屏数=%d" % (s, len(cfg["screens"])))
log("   data.json 文件存在=%s" % os.path.exists(df))

# 4) 空请求体 POST：应 400 且不改数据
s, b = req("POST", "/api/config", "")
log("4) POST 空请求体 -> %s, msg=%s" % (s, b))
s2, b2 = req("GET", "/api/config")
cfg2 = json.loads(b2)
log("   空POST后屏数仍为=%d（未被清空）" % len(cfg2["screens"]))

# 5) 非法 JSON POST：应 400 且不改数据
s, b = req("POST", "/api/config", "{bad json")
log("5) POST 非法JSON -> %s, msg=%s" % (s, b))
s2, b2 = req("GET", "/api/config")
log("   非法JSON后屏数仍为=%d" % len(json.loads(b2)["screens"]))

# 6) 静态页 / 后台可达
for p in ["/", "/index.html", "/admin.html", "/assets/css/style.css", "/manifest.webmanifest"]:
    s, _ = req("GET", p)
    log("6) GET %s -> %s" % (p, s))

# 7) OPTIONS 预检
s, _ = req("OPTIONS", "/api/config")
log("7) OPTIONS /api/config -> %s" % s)

# 8) 损坏的 data.json：应回退默认
with open(df, "w", encoding="utf-8") as f:
    f.write("{ 这不是合法 json ")
s, b = req("GET", "/api/config")
log("8) data.json 损坏后 GET -> %s, 屏数=%d(回退默认)" % (s, len(json.loads(b)["screens"])))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("DONE")
