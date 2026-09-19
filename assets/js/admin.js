(function () {
  'use strict';
  var listEl = document.getElementById('list');
  var form = document.getElementById('editForm');
  var fId = document.getElementById('fId');
  var fName = document.getElementById('fName');
  var fUrl = document.getElementById('fUrl');
  var fIcon = document.getElementById('fIcon');
  var fEnabled = document.getElementById('fEnabled');
  var titleInput = document.getElementById('titleInput');
  var resetBtn = document.getElementById('resetBtn');
  var msg = document.getElementById('msg');
  var modeTag = document.getElementById('modeTag');

  var screens = [];
  var title = '展厅控制中心';

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function truncate(s, n) { return s.length > n ? s.slice(0, n) + '…' : s; }

  function updateMode() {
    if (!modeTag) return;
    if (Store.getMode() === 'remote') {
      modeTag.textContent = '● 已连接服务器（多平板共享）';
      modeTag.className = 'mode-tag mode-remote';
    } else {
      modeTag.textContent = '● 本地缓存（未连服务器）';
      modeTag.className = 'mode-tag mode-local';
    }
  }

  function refresh() {
    Store.load().then(function (data) {
      screens = data.screens || [];
      title = data.title || '展厅控制中心';
      titleInput.value = title;
      renderList();
      updateMode();
    });
  }

  function persist() {
    Store.save({ title: title, screens: screens }).then(updateMode);
  }

  function renderList() {
    listEl.innerHTML = '';
    if (screens.length === 0) {
      listEl.innerHTML = '<tr><td colspan="3" class="muted">暂无屏幕，请在上方添加</td></tr>';
      return;
    }
    screens.forEach(function (s, i) {
      var tr = document.createElement('tr');
      var offTag = s.enabled === false ? ' <span class="tag-off">已隐藏</span>' : '';
      tr.innerHTML =
        '<td>' + (s.icon ? escapeHtml(s.icon) + ' ' : '') + escapeHtml(s.name) + offTag + '</td>' +
        '<td class="c-url"><a href="' + escapeHtml(s.url) + '" target="_blank" rel="noopener">' + escapeHtml(truncate(s.url, 42)) + '</a></td>' +
        '<td class="c-actions">' +
          '<button data-act="up" data-i="' + i + '" ' + (i === 0 ? 'disabled' : '') + ' title="上移">↑</button>' +
          '<button data-act="down" data-i="' + i + '" ' + (i === screens.length - 1 ? 'disabled' : '') + ' title="下移">↓</button>' +
          '<button data-act="edit" data-i="' + i + '">编辑</button>' +
          '<button data-act="del" data-i="' + i + '" class="danger">删除</button>' +
        '</td>';
      listEl.appendChild(tr);
    });
  }

  listEl.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    var i = +btn.dataset.i;
    var act = btn.dataset.act;
    if (act === 'up') move(i, -1);
    else if (act === 'down') move(i, 1);
    else if (act === 'edit') edit(i);
    else if (act === 'del') del(i);
  });

  function move(i, dir) {
    var j = i + dir;
    if (j < 0 || j >= screens.length) return;
    var t = screens[i]; screens[i] = screens[j]; screens[j] = t;
    persist(); renderList(); flash('已调整顺序');
  }

  function edit(i) {
    var s = screens[i];
    fId.value = s.id; fName.value = s.name; fUrl.value = s.url; fIcon.value = s.icon || '';
    fEnabled.checked = s.enabled !== false;
    form.scrollIntoView({ behavior: 'smooth' });
    fName.focus();
  }

  function del(i) {
    if (!confirm('确认删除「' + screens[i].name + '」？')) return;
    screens.splice(i, 1);
    persist(); renderList(); flash('已删除');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = fName.value.trim();
    var url = fUrl.value.trim();
    if (!name) { alert('请填写屏幕名称'); return; }
    if (!url) { alert('请填写链接'); return; }
    var id = fId.value;
    if (id) {
      var s = screens.find(function (x) { return x.id === id; });
      if (s) { s.name = name; s.url = url; s.icon = fIcon.value.trim(); s.enabled = fEnabled.checked; }
      flash('已保存修改');
    } else {
      screens.push({ id: Store.uid(), name: name, url: url, icon: fIcon.value.trim(), enabled: fEnabled.checked });
      flash('已新增屏幕');
    }
    persist();
    resetForm(); renderList();
  });

  function resetForm() {
    fId.value = ''; fName.value = ''; fUrl.value = ''; fIcon.value = ''; fEnabled.checked = true;
  }

  resetBtn.addEventListener('click', resetForm);

  titleInput.addEventListener('change', function () {
    title = titleInput.value.trim() || '展厅控制中心';
    persist(); flash('展厅名称已更新');
  });

  var flashTimer;
  function flash(t) {
    msg.textContent = t;
    msg.classList.add('show');
    clearTimeout(flashTimer);
    flashTimer = setTimeout(function () { msg.classList.remove('show'); }, 1800);
  }

  refresh();

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }
})();
