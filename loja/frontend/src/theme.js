const KEY = "setsync-theme";

export function lerTema() {
  try {
    const v = localStorage.getItem(KEY);
    if (v === "light" || v === "dark") return v;
    const cookie = document.cookie.match(/(?:^|; )setsync-theme=(dark|light)/);
    if (cookie) return cookie[1];
  } catch {
    /* ignore */
  }
  return "dark";
}

export function aplicarTema(tema) {
  const t = tema === "light" ? "light" : "dark";
  const root = document.documentElement;
  root.setAttribute("data-theme", t);
  root.classList.toggle("dark", t === "dark");
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", t === "dark" ? "#0b1422" : "#f3f4f6");
  try {
    localStorage.setItem(KEY, t);
    document.cookie = `${KEY}=${t}; Domain=.unissono.app; Path=/; Max-Age=31536000; SameSite=Lax`;
  } catch {
    /* ignore */
  }
  return t;
}
