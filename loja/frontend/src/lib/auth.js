const APP = "https://unissono.app";
const LOJA = "https://loja.unissono.app";

export const LOGIN_URL = `${APP}/auth/login?next=${encodeURIComponent(LOJA)}`;
export const ADMIN_LOGIN_URL = `${APP}/auth/login?next=${encodeURIComponent(`${LOJA}/admin`)}`;
export const REGISTER_URL = `${APP}/auth/register?next=${encodeURIComponent(LOJA)}`;
export const LOGOUT_URL = `${APP}/auth/sair?next=${encodeURIComponent(LOJA)}`;
export const CONTA_URL = `${APP}/auth/perfil`;

export async function carregarSessao() {
  try {
    const res = await fetch(`${APP}/auth/me`, { credentials: "include", cache: "no-store" });
    if (!res.ok) return { autenticado: false };
    const data = await res.json();
    if (!data?.autenticado) return { autenticado: false };
    const usuario = data.usuario || {};
    return {
      autenticado: true,
      usuario: {
        ...usuario,
        is_superadmin: Boolean(usuario.is_superadmin || usuario.is_loja_admin),
        is_loja_admin: Boolean(usuario.is_superadmin || usuario.is_loja_admin),
      },
      token: data.loja_token || "",
    };
  } catch {
    return { autenticado: false };
  }
}
