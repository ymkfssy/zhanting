#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""展厅控制中心 · 极简共享数据服务器（仅依赖 Python 标准库）

把屏幕菜单保存在服务器上的明文文件 data.json 中。
多台平板访问同一个地址（http://<服务器IP>:端口），即可共享同一份菜单。

启动：
    python server.py
指定监听地址 / 端口：
    python server.py --host 0.0.0.0 --port 8123

平板访问： http://<服务器IP>:8123
"""
import argparse
import json
import os
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
API_PATH = '/api/config'

WELCOME_HTML = (
    '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<style>body{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;'
    'background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:#fff;'
    'display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;text-align:center}'
    'h1{font-size:2.6rem;margin:0 0 .35em;letter-spacing:2px} p{opacity:.8;font-size:1.15rem;margin:0}</style></head>'
    '<body><h1>欢迎来到展厅</h1><p>请在左侧选择需要展示的屏幕</p></body></html>'
)
WELCOME_URL = 'data:text/html;charset=utf-8,' + urllib.parse.quote(WELCOME_HTML)

DEFAULT_CONFIG = {
    'title': '展厅控制中心',
    'screens': [
        {'id': 's_welcome', 'name': '欢迎页', 'url': WELCOME_URL, 'icon': '🏠', 'enabled': True},
        {'id': 's_data', 'name': '数据大屏', 'url': 'https://example.com', 'icon': '📊', 'enabled': True},
        {'id': 's_video', 'name': '宣传视频', 'url': 'https://example.com', 'icon': '🎬', 'enabled': True},
        {'id': 's_monitor', 'name': '实时监控', 'url': 'https://example.com', 'icon': '📡', 'enabled': True},
    ],
}


def normalize(cfg):
    """把任意输入规整成 {title, screens[]}，防止脏数据让前端崩溃。"""
    cfg = cfg if isinstance(cfg, dict) else {}
    screens = cfg.get('screens') if isinstance(cfg.get('screens'), list) else []
    out = []
    for i, s in enumerate(screens):
        if not isinstance(s, dict):
            continue
        out.append({
            'id': str(s.get('id') or ('s_' + str(i))),
            'name': str(s.get('name') or '未命名'),
            'url': str(s.get('url') or ''),
            'icon': str(s.get('icon') or '📺'),
            'enabled': bool(s.get('enabled', True)),
        })
    return {
        'title': str(cfg.get('title') or '展厅控制中心'),
        'screens': out,
    }


def load_config():
    """读取 data.json；文件不存在或损坏时写入默认配置。"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        if isinstance(cfg, dict):
            return normalize(cfg)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    save_config(DEFAULT_CONFIG)
    return normalize(DEFAULT_CONFIG)


def save_config(cfg):
    """原子写入 data.json（先写临时文件再替换，避免写一半被读到）。"""
    cfg = normalize(cfg)
    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)
    return cfg


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        # 允许跨域，方便把前端放其他来源时也能读写接口
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == API_PATH:
            self._send_json(load_config())
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split('?', 1)[0]
        if path == API_PATH:
            length = int(self.headers.get('Content-Length', 0) or 0)
            raw = self.rfile.read(length) if length else b''
            if not raw:
                self._send_json({'error': '请求体为空，未做任何修改'}, 400)
                return
            try:
                data = json.loads(raw.decode('utf-8'))
            except Exception:
                self._send_json({'error': '请求体不是合法 JSON'}, 400)
                return
            self._send_json(save_config(data))
            return
        self._send_json({'error': '不支持的请求'}, 405)

    def do_OPTIONS(self):
        path = self.path.split('?', 1)[0]
        if path == API_PATH:
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        self.send_response(405)
        self.end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('[展厅服务器] ' + (fmt % args) + '\n')


def main():
    p = argparse.ArgumentParser(description='展厅控制中心共享数据服务器')
    p.add_argument('--host', default='0.0.0.0', help='监听地址，默认 0.0.0.0（所有网卡）')
    p.add_argument('--port', type=int, default=8123, help='监听端口，默认 8123')
    args = p.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    httpd.allow_reuse_address = True
    print('展厅控制中心服务器已启动')
    print('  本机访问： http://localhost:%d' % args.port)
    print('  平板访问： http://<本机IP>:%d  （需与服务器同一局域网）' % args.port)
    print('  数据存储： %s （明文 JSON）' % DATA_FILE)
    print('  按 Ctrl+C 停止')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
        httpd.server_close()


if __name__ == '__main__':
    main()
