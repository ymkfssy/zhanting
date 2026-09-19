(function () {
  'use strict';
  var nav = document.getElementById('sidenav');
  var frame = document.getElementById('frame');
  var brand = document.getElementById('brandTitle');
  var currentName = document.getElementById('currentName');
  var openBtn = document.getElementById('openNew');

  var screens = [];
  var activeId = null;
  var activeUrl = '';

  function visibleScreens() {
    return screens.filter(function (s) { return s.enabled !== false; });
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function render(data) {
    screens = data.screens || [];
    var title = data.title || '展厅控制中心';
    brand.textContent = title;
    document.title = title;
    nav.innerHTML = '';
    var vis = visibleScreens();
    if (vis.length === 0) {
      nav.innerHTML = '<div class="empty">暂无屏幕<br>请到后台添加</div>';
      frame.src = 'about:blank';
      currentName.textContent = '未选择';
      activeId = null;
      activeUrl = '';
      return;
    }
    vis.forEach(function (s) {
      var btn = document.createElement('button');
      btn.className = 'nav-item';
      btn.type = 'button';
      btn.setAttribute('title', s.name);
      btn.innerHTML = '<span class="nav-icon">' + (s.icon || '📺') + '</span>' +
        '<span class="nav-label">' + escapeHtml(s.name) + '</span>';
      btn.addEventListener('click', function () { activate(s.id); });
      nav.appendChild(btn);
    });
    if (!activeId || !vis.some(function (s) { return s.id === activeId; })) {
      activate(vis[0].id);
    } else {
      var cur = screens.find(function (x) { return x.id === activeId; });
      if (cur && cur.url !== activeUrl) activate(activeId); // 后台改了链接则刷新
      else markActive();
    }
  }

  function activate(id) {
    var s = screens.find(function (x) { return x.id === id; });
    if (!s) return;
    activeId = id;
    activeUrl = s.url;
    frame.src = s.url;
    currentName.textContent = s.name;
    openBtn.onclick = function () { window.open(s.url, '_blank'); };
    markActive();
  }

  function markActive() {
    var vis = visibleScreens();
    Array.prototype.forEach.call(nav.children, function (el, i) {
      if (vis[i] && vis[i].id === activeId) el.classList.add('active');
      else el.classList.remove('active');
    });
  }

  function loadAndRender() {
    Store.load().then(render);
  }

  loadAndRender();

  // 后台修改后，回到前台自动刷新
  window.addEventListener('focus', loadAndRender);
  window.addEventListener('storage', loadAndRender);

  // 多平板共享：定时向服务器拉取最新菜单（别人在后台改了也能同步）
  setInterval(loadAndRender, 15000);

  // 注册 PWA Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }
})();
