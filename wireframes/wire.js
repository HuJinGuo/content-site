// ai.nornless.com 线框壳：注入顶栏 / 页脚 / 后台侧栏 / 线框工具条。
// <body data-shell="site|app|ads|studio|admin" data-active="<nav key>" data-user="1（登录态）">
// 工具条：索引 · 主题 · 标注 开/关 · 开关态 关闭/开启（?flags=on 可强制，截图用）。
(function () {
  var NAV_SITE = [
    ['learn', '学习', 'site-learn.html'],
    ['news', '情报', 'site-news.html'],
    ['tools', '工具', 'site-tools.html'],
    ['glossary', '百科', 'site-glossary.html'],
    ['jobs', '招聘', 'site-jobs.html', 'ads.self_serve.jobs'],
    ['search', '搜索', 'site-search.html']
  ];
  var NAV_APP = [
    ['app', '学习台', 'app-home.html'],
    ['library', '收藏与划线', 'app-library.html'],
    ['briefing', '简报', 'app-library.html#briefing'],
    ['downloads', '下载', 'app-library.html#downloads'],
    ['ask', '问答', 'app-ask.html', 'ask.enabled'],
    ['account', '账户', 'app-account.html']
  ];
  var NAV_STUDIO = [
    { t: '编辑部', items: [
      ['home', '工作台', 'studio-home.html'],
      ['topics', '选题池 · 缺口', 'studio-topics.html'],
      ['briefs', 'Brief', 'studio-brief.html'],
      ['generate', '生成台 · 成本', 'studio-generate.html'],
      ['editor', '稿件编辑器', 'studio-editor.html'],
      ['qa', '机审 · 事实清单', 'studio-qa.html'],
      ['review', '审稿列表', 'studio-review.html', 12],
      ['issues', '期刊编排', 'studio-issue.html']
    ] },
    { t: '维护', items: [
      ['graph', '图谱维护', 'studio-graph.html'],
      ['sources', '情报源', 'studio-sources.html'],
      ['entities', '实体 · 工具目录', 'studio-entities.html'],
      ['refresh', '保鲜队列', 'studio-refresh.html', 7],
      ['errata', '勘误 · 反馈', 'studio-errata.html', 3],
      ['assets', '资产', 'studio-assets.html'],
      ['prompts', '提示词 · 模板版本', 'studio-prompts.html']
    ] }
  ];
  var NAV_ADMIN = [
    { t: '用户与权益', items: [
      ['users', '用户 · 权益', 'admin-users.html'],
      ['codes', '码 · 对账', 'admin-codes.html'],
      ['paywall', '付费墙 · 收费清单', 'admin-paywall.html']
    ] },
    { t: '广告', items: [
      ['ads', '广告位 · 排期 · 广告主', 'admin-ads.html'],
      ['ads-review', '素材审核', 'admin-ads-review.html', 4],
      ['zones', '专区条目审核', 'admin-zones.html', 6]
    ] },
    { t: '运营', items: [
      ['mail', '邮件', 'admin-mail.html'],
      ['flags', '功能开关', 'admin-flags.html'],
      ['metrics', '达标线 · 看板', 'admin-metrics.html'],
      ['seo', 'SEO', 'admin-seo.html']
    ] },
    { t: '系统', items: [
      ['system', '任务 · 成本 · 备份', 'admin-system.html'],
      ['audit', '审计日志', 'admin-audit.html'],
      ['settings', '站点设置', 'admin-settings.html']
    ] }
  ];
  var NAV_ADS = [
    { t: '广告主', items: [
      ['dashboard', '我的投放', 'ads-dashboard.html'],
      ['new', '新建投放', 'ads-new.html'],
      ['campaign', '活动详情 · 报表', 'ads-campaign.html'],
      ['billing', '兑码记录 · 收据', 'ads-billing.html']
    ] }
  ];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function topbar(active, user, shellKind) {
    var links = NAV_SITE.map(function (n) {
      var cls = (n[0] === active ? 'active' : '');
      var gated = n[3] ? ' gated inline' : '';
      var flag = n[3] ? ' data-flag="' + n[3] + '"' : '';
      return '<a class="' + cls + gated + '" href="' + n[2] + '"' + flag + '>' + esc(n[1]) + '</a>';
    }).join('');
    var right = user
      ? '<a class="avatar" href="app-home.html" title="学习台">读</a>'
      : '<a class="btn small" href="site-login.html">登录</a>';
    return '<header class="topbar">' +
      '<a class="brand" href="site-home.html"><span class="brand-mark"></span><span><span class="name">ai.nornless.com</span><span class="sub">AI 知识阶梯 · 科技情报</span></span></a>' +
      '<nav>' + links + '</nav>' +
      '<div class="actions">' +
      '<button class="icon-btn" data-theme-toggle>☀ 浅</button>' +
      right +
      '</div></header>';
  }

  function footer() {
    return '<footer class="footer container">' +
      '<span>ai.nornless.com</span>' +
      '<a href="site-static.html#about">关于</a><a href="site-static.html#disclosure">AI 使用披露</a><a href="site-static.html#ads-policy">广告政策</a>' +
      '<a href="site-static.html#license">许可</a><a href="site-static.html#privacy">隐私</a><a href="site-static.html#errata">勘误</a><a href="site-static.html#changelog">更新日志</a>' +
      '<a href="site-subscribe.html">RSS · 邮件</a>' +
      '<a class="gated inline" data-flag="supporter.enabled" href="site-pricing.html">支持者</a>' +
      '<a class="gated inline" data-flag="ads.enabled" href="site-advertise.html">在 ai.nornless.com 投放</a>' +
      '<span class="right">境外起站 · 暂不备案 · 内容 CC BY-NC-ND 4.0</span>' +
      '</footer>';
  }

  function subnav(active) {
    return '<div class="subnav">' + NAV_APP.map(function (n) {
      var gated = n[3] ? ' class="gated inline' + (n[0] === active ? ' active' : '') + '" data-flag="' + n[3] + '"' : (n[0] === active ? ' class="active"' : '');
      return '<a href="' + n[2] + '"' + gated + '>' + esc(n[1]) + '</a>';
    }).join('') + '</div>';
  }

  function sidebar(groups, active, title, sub, foot) {
    var html = '<div class="logo"><span class="brand-mark"></span><span><div>' + esc(title) + '</div><div class="muted small" style="font-weight:500">' + esc(sub) + '</div></span></div>';
    groups.forEach(function (g) {
      html += '<div class="nav-mod-title">' + esc(g.t) + '</div>';
      g.items.forEach(function (n) {
        html += '<a class="nav-btn' + (n[0] === active ? ' active' : '') + '" href="' + n[2] + '">' + esc(n[1]) + (n[3] ? '<span class="badge">' + n[3] + '</span>' : '') + '</a>';
      });
    });
    html += '<div class="side-foot">' + foot + '</div>';
    return html;
  }

  function wfbar() {
    return '<div class="wf-bar">' +
      '<a href="index.html">线框索引</a>' +
      '<span class="sep"></span>' +
      '<button data-wf-theme>☀ 浅</button>' +
      '<button data-wf-anno>标注</button>' +
      '<button data-wf-flags>开关态：关闭</button>' +
      '</div>';
  }

  function setTheme(t) {
    document.documentElement.classList.toggle('dark', t === 'dark');
    localStorage.setItem('theme', t);
    document.querySelectorAll('[data-theme-toggle],[data-wf-theme]').forEach(function (b) { b.textContent = t === 'dark' ? '☾ 深' : '☀ 浅'; });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var body = document.body;
    var shell = body.getAttribute('data-shell') || 'site';
    var active = body.getAttribute('data-active') || '';
    var user = body.getAttribute('data-user') === '1';
    var q = new URLSearchParams(location.search);

    if (shell === 'site' || shell === 'app') {
      body.insertAdjacentHTML('afterbegin', topbar(shell === 'app' ? '' : active, user || shell === 'app'));
      var main = document.querySelector('main');
      if (main) {
        if (shell === 'app') main.insertAdjacentHTML('afterbegin', subnav(active));
        main.insertAdjacentHTML('afterend', footer());
      }
    } else {
      var sb = document.getElementById('sidebar');
      if (sb) {
        if (shell === 'studio') sb.innerHTML = sidebar(NAV_STUDIO, active, 'Studio 编辑部', 'ai.nornless.com', '<span>主编 · Publisher</span><span class="muted">TOTP 已验证 · 会话 12h</span><a href="site-home.html">← 看前台</a>');
        if (shell === 'admin') sb.innerHTML = sidebar(NAV_ADMIN, active, 'Admin 运营', 'ai.nornless.com', '<span>站长 · Admin</span><span class="muted">TOTP 已验证 · 会话 12h</span><a href="site-home.html">← 看前台</a>');
        if (shell === 'ads') sb.innerHTML = sidebar(NAV_ADS, active, '广告主门户', 'ai.nornless.com / ads', '<span>某某科技 · 广告主</span><span class="muted">主体已核验</span><a href="site-advertise.html">← 媒体页</a>');
      }
    }

    body.insertAdjacentHTML('beforeend', wfbar());

    // 标注
    var annoOff = q.get('anno') === 'off' || localStorage.getItem('wf-anno') === 'off';
    body.classList.toggle('hide-anno', annoOff);
    var ab = document.querySelector('[data-wf-anno]');
    function paintAnno() { ab.classList.toggle('on', !body.classList.contains('hide-anno')); ab.textContent = body.classList.contains('hide-anno') ? '标注：隐藏' : '标注：显示'; }
    paintAnno();
    ab.addEventListener('click', function () { body.classList.toggle('hide-anno'); localStorage.setItem('wf-anno', body.classList.contains('hide-anno') ? 'off' : 'on'); paintAnno(); });

    // 开关态
    var flagsOn = q.get('flags') === 'on' || (q.get('flags') !== 'off' && localStorage.getItem('wf-flags') === 'on');
    body.classList.toggle('flags-on', flagsOn);
    var fb = document.querySelector('[data-wf-flags]');
    function paintFlags() { var on = body.classList.contains('flags-on'); fb.classList.toggle('on', on); fb.textContent = on ? '开关态：开启（ads 等全开）' : '开关态：关闭（默认）'; }
    paintFlags();
    fb.addEventListener('click', function () { body.classList.toggle('flags-on'); localStorage.setItem('wf-flags', body.classList.contains('flags-on') ? 'on' : 'off'); paintFlags(); });

    // 主题（与 theme.js 共用 localStorage.theme；这里只接管工具条按钮）
    var tb = document.querySelector('[data-wf-theme]');
    setTheme(document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    tb.addEventListener('click', function () { setTheme(document.documentElement.classList.contains('dark') ? 'light' : 'dark'); });

    // 文章页伴读卡：快捷问题直接填入输入框，方便在线框里演示真实交互。
    document.querySelectorAll('.article-ai-prompts button').forEach(function (button) {
      button.addEventListener('click', function () {
        var card = button.closest('.article-ai-card');
        var input = card && card.querySelector('textarea');
        if (input) { input.value = button.textContent.trim(); input.focus(); }
      });
    });
  });
})();
