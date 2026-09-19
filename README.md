# 展厅控制中心

一个简单的展厅多屏幕控制页面。包含「前台展示」与「后台管理」两个互相独立的页面，二者通过浏览器本地存储（localStorage）共享数据,**无需任何服务器**。
配套软件地址https://www.tree666.com/post/158.html

## 目录结构

```
展厅控制/
├── index.html            # 前台展示页（平板大屏用）
├── admin.html            # 后台管理页（新增/编辑/删除/排序）
├── manifest.webmanifest  # PWA 应用清单
├── sw.js                 # Service Worker（离线缓存）
├── assets/
│   ├── css/style.css
│   ├── js/store.js       # 前后台共用的本地存储
│   ├── js/app.js         # 前台逻辑
│   ├── js/admin.js       # 后台逻辑
│   └── icons/            # 应用图标
└── README.md
```

## 使用说明

- **前台（index.html）**：平板横屏展示。左侧导航约占整体宽度 10%，点击菜单项，右侧 `iframe` 载入对应链接。顶部「⚙」可进入后台；若目标网站禁止被 `iframe` 嵌入，可点「↗ 新窗口」按钮打开。
- **后台（admin.html）**：设置展厅名称；对每个屏幕进行新增、编辑、删除，并用「↑ / ↓」调整顺序。修改保存后，回到前台会自动刷新。

## 打包为 APP

本系统已配置为 **PWA（渐进式 Web 应用）**，可离线运行、可“安装”到平板主屏。

**方式一 · 零构建（推荐）**
在平板浏览器中打开 `index.html`（需通过 http/https 访问，见下方部署提示），选择“添加到主屏幕”（Android Chrome）或“添加到主屏幕”（iPad Safari），即可获得一个全屏、可离线的 APP。

**方式二 · 生成 Android APK（TWA）**
将本目录部署到一个 https 地址后，使用 [PWABuilder](https://www.pwabuilder.com) 一键生成 Android 安装包；本地也可执行 `npx @pwabuilder/cli` 或 Google 的 Bubblewrap。

**方式三 · 原生壳（iOS / Android）**
用 Capacitor 将本目录作为 `webDir` 打包为原生应用：
```
npm init -y && npm i @capacitor/core @capacitor/cli
npx cap init 展厅控制 com.example.exhibit --web-dir .
npx cap add android   # 或 ios
npx cap sync && npx cap open android
```

## 部署提示

- Service Worker 必须通过 `http://` 或 `https://` 访问（`localhost` 亦可），**不能直接用 `file://` 双击打开**。
- 本地快速预览：在目录内执行 `python -m http.server 8123`，浏览器访问 `http://localhost:8123`。
- 部分网站设置了 `X-Frame-Options` / `CSP frame-ancestors` 会拒绝被 `iframe` 嵌入，此时请使用「新窗口」按钮，或改用允许嵌入的内部页面/视频流地址。

---

## 多平板共享（服务器模式 · 推荐展厅使用）

默认已开启「服务器模式」：数据不再存在每台平板的浏览器里，而是集中保存在**一台共用服务器**的明文文件 `data.json` 中。任一台平板在后台改了菜单，其他平板前台每 15 秒自动同步。

### 1. 启动服务器（只需一台电脑/一台平板长期开机即可）

进入本目录，用 Python 标准库启动（无需安装任何依赖）：

```bash
python server.py
```

默认监听 `0.0.0.0:8123`（所有网卡）。如需指定端口：

```bash
python server.py --host 0.0.0.0 --port 8080
```

启动后控制台会打印本机与平板访问地址。首次访问时，`data.json` 会被自动创建并写入默认示例菜单（4 个屏幕）。

### 2. 平板访问

让所有平板连到**同一局域网**，浏览器打开：

```
http://<服务器IP>:8123
```

- 前台：`http://<服务器IP>:8123/`
- 后台：`http://<服务器IP>:8123/admin.html`

后台右上角会显示「● 已连接服务器（多平板共享）」或断网时的「● 本地缓存」，便于判断状态。

### 3. 数据文件（明文）

所有菜单配置就在这个文件里，纯文本 JSON，可直接用记事本编辑：

```
展厅控制/data.json
```

结构示例：

```json
{
  "title": "展厅控制中心",
  "screens": [
    { "id": "s_welcome", "name": "欢迎页", "url": "…", "icon": "🏠", "enabled": true },
    { "id": "s_data",    "name": "数据大屏", "url": "https://…", "icon": "📊", "enabled": true }
  ]
}
```

### 4. 如何切换回“单机模式”

打开 `assets/js/store.js`，把顶部 `var USE_REMOTE = true;` 改成 `false`，即可退回每台平板各自用浏览器本地存储、互不共享的旧模式。

### 5. 注意事项

- 服务器那台机器要长期开机、不休眠；它一关，平板后台就保存不进去（前台仍可用本地缓存展示）。
- 当前为明文、无鉴权，仅适合**内部局域网**使用，请勿直接暴露在公网。
- 若服务器与平板不在同一网段（如跨 VLAN / 经路由器隔离），需在网络设备上放行对应端口，或把服务器部署在与平板同网段。
- `data.json` 是数据，误删会让菜单回到默认示例；建议定期备份该文件。
- 感谢树先生无私奉献，树先生官网https://www.tree666.com/
