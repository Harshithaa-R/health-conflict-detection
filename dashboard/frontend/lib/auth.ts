export type Role = "admin" | "reviewer" | "analyst" | "chw";
export type AuthUser = {
  email: string;
  name: string;
  role: Role;
  assigned_villages?: string[];
  accessToken: string;
  expiresAt: number;
};

const KEY = "healthsync-session";
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export function getSession(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const session = JSON.parse(raw) as AuthUser;
    if (!session.accessToken || !session.expiresAt || Date.now() >= session.expiresAt) {
      localStorage.removeItem(KEY);
      return null;
    }
    return session;
  } catch {
    localStorage.removeItem(KEY);
    return null;
  }
}

export function saveSession(data: {access_token: string; expires_at: string; user: Omit<AuthUser, "accessToken" | "expiresAt">}) {
  const session: AuthUser = {
    ...data.user,
    accessToken: data.access_token,
    expiresAt: new Date(data.expires_at).getTime(),
  };
  localStorage.setItem(KEY, JSON.stringify(session));
  return session;
}

export function clearSession() {
  if (typeof window !== "undefined") localStorage.removeItem(KEY);
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const session = getSession();
  const headers = new Headers(init.headers);
  if (session?.accessToken) headers.set("Authorization", `Bearer ${session.accessToken}`);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_BASE}${path}`, {...init, headers, cache: "no-store"});
  if (response.status === 401 && typeof window !== "undefined") {
    clearSession();
    window.location.assign("/login?expired=1");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}
