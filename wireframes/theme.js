// 主题切换：html.dark + localStorage.theme；?theme=dark|light 可强制（截图用）。
(function () {
  var KEY = 'theme';
  var q = new URLSearchParams(location.search).get('theme');
  var saved = localStorage.getItem(KEY);
  var prefers = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  var theme = (q === 'dark' || q === 'light') ? q : (saved === 'dark' || saved === 'light') ? saved : prefers;
  apply(theme);

  function apply(t) {
    document.documentElement.classList.toggle('dark', t === 'dark');
    localStorage.setItem(KEY, t);
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.textContent = t === 'dark' ? '☾ 深' : '☀ 浅';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    apply(document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.addEventListener('click', function () {
        apply(document.documentElement.classList.contains('dark') ? 'light' : 'dark');
      });
    });
  });
})();
