"use client";

import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { API_BASE, saveSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("admin@karnataka.gov.in");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [resetMessage, setResetMessage] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password}),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Unable to sign in");
      saveSession(body);
      router.replace("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to reach the API. Is FastAPI running on port 8000?");
    } finally {
      setBusy(false);
    }
  }

  async function requestReset() {
    setError("");
    setResetMessage("");
    try {
      const response = await fetch(`${API_BASE}/auth/password-reset`, {
        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email}),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Reset request failed");
      setResetMessage(`${body.message} Password reset delivery must be configured by an administrator.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not request reset");
    }
  }

  return <main className="login-shell"><section className="login-card">
    <div className="brand"><span className="brand-mark">H</span><div><b>HealthSync</b><small>KARNATAKA HUB</small></div></div>
    <p className="eyebrow">SECURE STAFF ACCESS</p><h1>Welcome back</h1>
    <p className="muted">Sign in to review health-record conflicts and patient alerts.</p>
    {params.get("expired") && <div className="notice">Your session expired. Please sign in again.</div>}
    <form onSubmit={submit} className="stack">
      <label>Email address<input type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} /></label>
      <label>Password<input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} /></label>
      {error && <div className="error" role="alert">{error}</div>}
      {resetMessage && <div className="notice" role="status">{resetMessage}</div>}
      <button className="primary-button" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
    </form>
    <button className="link-button" onClick={requestReset} type="button">Forgot password?</button>
    <p className="demo-hint">Local demo accounts: admin / reviewer / analyst / chw. Use the email shown in the code and their development password.</p>
    <p className="small muted">Role-based demo access · Sessions expire after 8 hours · SSO can be added later</p>
  </section></main>;
}
