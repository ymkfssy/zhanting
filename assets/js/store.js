(function () {
  'use strict';
  var SCREENS_KEY = 'exhibit_screens_v1';
  var TITLE_KEY = 'exhibit_title_v1';
  var API_URL = 'api/config';

  // true  = 数据存在服务器（多台平板共享同一份菜单）
  // false = 数据仍存在本机浏览器（单机模式，无需服务器）
  var USE_REMOTE = true;

  var lastMode = 'local';

  function uid() {
    return 's_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }

  function seedScreens() {
    var welcome = [
      '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
      '<meta name="viewport" content="width=device-width,initial-scale=1">',
      '<style>body{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;',
      'background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:#fff;',
      'display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;text-align:center}',
      'h1{font-size:2.6rem;margin:0 0 .35em;letter-spacing:2px} p{opacity:.8;font-size:1.15rem;margin:0}</style></head>',
      '<body><h1>欢迎来到展厅</h1><p>请在左侧选择需要展示的屏幕</p></body></html>'
    ].join('');
    var welcomeUrl = 'data:text/html;charset=utf-8,' + encodeURIComponent(welcome);
    return [
      { id: uid(), name: '欢迎页', url: welcomeUrl, icon: '🏠', enabled: true },
      { id: uid(), name: '数据大屏', url: 'https://example.com', icon: '📊', enabled: true },
      { id: uid(), name: '宣传视频', url: 'https://example.com', icon: '🎬', enabled: true },
      { id: uid(), name: '实时监控', url: 'https://example.com', icon: '📡', enabled: true }
    ];
  }

  function loadTitleLocal() {
    return localStorage.getItem(TITLE_KEY) || '展厅控制中心';
  }

  function mirrorLocal(cfg) {
    try {
      localStorage.setItem(SCREENS_KEY, JSON.stringify(cfg.screens));
      localStorage.setItem(TITLE_KEY, cfg.title);
    } catch (e) {}
  }

  function readLocal() {
    try {
      var raw = localStorage.getItem(SCREENS_KEY);
      if (raw) {
        var list = JSON.parse(raw);
        if (Array.isArray(list)) return list;
      }
    } catch (e) {}
    var seed = seedScreens();
    mirrorLocal({ title: loadTitleLocal(), screens: seed });
    return seed;
  }

  function normalize(cfg) {
    cfg = cfg || {};
    var screens = Array.isArray(cfg.screens) ? cfg.screens : [];
    screens = screens.map(function (s) {
      return {
        id: s.id || uid(),
        name: String(s.name || '未命名'),
        url: String(s.url || ''),
        icon: s.icon || '📺',
        enabled: s.enabled !== false
      };
    });
    return { title: String(cfg.title || '展厅控制中心'), screens: screens };
  }

  // 读取完整配置：{ title, screens }
  function load() {
    if (USE_REMOTE) {
      return fetch(API_URL, { cache: 'no-store' })
        .then(function (r) {
          if (!r.ok) throw new Error('http ' + r.status);
          return r.json();
        })
        .then(function (cfg) {
          cfg = normalize(cfg);
          lastMode = 'remote';
          mirrorLocal(cfg); // 顺手镜像到本地，断网时仍可展示
          return cfg;
        })
        .catch(function () {
          lastMode = 'local'; // 连不上服务器，退回本机缓存
          return { title: loadTitleLocal(), screens: readLocal() };
        });
    }
    lastMode = 'local';
    return Promise.resolve({ title: loadTitleLocal(), screens: readLocal() });
  }

  // 保存完整配置：{ title, screens }
  function save(cfg) {
    cfg = normalize(cfg);
    mirrorLocal(cfg);
    if (USE_REMOTE) {
      return fetch(API_URL, {
        method: 'POST',
        cache: 'no-store',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify(cfg)
      })
        .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); lastMode = 'remote'; return cfg; })
        .catch(function () { lastMode = 'local'; return cfg; });
    }
    lastMode = 'local';
    return Promise.resolve(cfg);
  }

  window.Store = {
    uid: uid,
    load: load,
    save: save,
    getMode: function () { return lastMode; }
  };
})();
