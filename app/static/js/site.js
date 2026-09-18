(function () {
  var t = localStorage.getItem("theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  function apply(v) {
    document.documentElement.classList.toggle("dark", v === "dark");
    localStorage.setItem("theme", v);
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.textContent = v === "dark" ? "深色" : "浅色";
    });
  }
  apply(t);
  var bar = document.querySelector(".banner.notice");
  if (bar) {
    var d = Number(localStorage.getItem("notice-dismissed") || 0);
    if (d && Date.now() - d < 7 * 24 * 3600 * 1000) bar.remove();
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-theme-toggle]");
    if (!b) return;
    apply(document.documentElement.classList.contains("dark") ? "light" : "dark");
  });
  document.addEventListener("click", function (e) {
    var x = e.target.closest("[data-dismiss-notice]");
    if (!x) return;
    localStorage.setItem("notice-dismissed", String(Date.now()));
    var notice = document.querySelector(".banner.notice");
    if (notice) notice.remove();
  });
  document.body.addEventListener("htmx:configRequest", function (evt) {
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) evt.detail.headers["X-CSRFToken"] = meta.content;
  });
  var READ_KEY = "nornless-read";
  function readList() {
    try {
      return JSON.parse(localStorage.getItem(READ_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }
  function saveRead(list) {
    localStorage.setItem(READ_KEY, JSON.stringify(list));
  }
  document.addEventListener("submit", function (e) {
    var form = e.target.closest("[data-read-form]");
    if (!form) return;
    var slug = form.getAttribute("data-slug");
    if (!slug) return;
    var undo = form.getAttribute("data-undo") === "1";
    var list = readList().filter(function (s) {
      return s !== slug;
    });
    if (!undo) list.push(slug);
    saveRead(list);
  });
})();
