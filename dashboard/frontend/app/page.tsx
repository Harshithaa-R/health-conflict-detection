"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, clearSession, getSession, AuthUser } from "@/lib/auth";

type Summary = {total_patients:number; high_risk_patients:number; normal_patients:number; patients_analysed:number; patients_with_conflicts:number; conflict_rate:number};
type ConflictSummary = {patients_analysed:number; patients_with_conflicts:number; resolved_conflicts:number};
type QueueRow = {patient_id:string; name?:string; district?:string; village?:string; conflict_types?:string; num_conflicts?:number; review_status?:string; [key:string]:unknown};
type Reliability = {cadre:string; source_reliability:number};
type QueueResponse = {total:number; records:QueueRow[]};

const panel: React.CSSProperties = {background:"#0f1623",border:"1px solid rgba(255,255,255,.08)",borderRadius:14,padding:20};

export default function DashboardPage() {
  const router = useRouter();
  const [user,setUser] = useState<AuthUser|null>(null);
  const [summary,setSummary] = useState<Summary|null>(null);
  const [conflictSummary,setConflictSummary] = useState<ConflictSummary|null>(null);
  const [queue,setQueue] = useState<QueueRow[]>([]);
  const [reliability,setReliability] = useState<Reliability[]>([]);
  const [search,setSearch] = useState("");
  const [district,setDistrict] = useState("");
  const [statusFilter,setStatusFilter] = useState("pending");
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");
  const [selected,setSelected] = useState<QueueRow|null>(null);
  const [reason,setReason] = useState("Clinician confirmation");
  const [source,setSource] = useState("PHC");
  const [value,setValue] = useState("");
  const [notes,setNotes] = useState("");
  const [actionBusy,setActionBusy] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session) { router.replace("/login"); return; }
    setUser(session);
  }, [router]);

  const loadData = useCallback(async () => {
    if (!user) return;
    setLoading(true); setError("");
    try {
      const params = new URLSearchParams({limit:"100", status:statusFilter});
      if (search.trim()) params.set("search",search.trim());
      if (district.trim()) params.set("district",district.trim());
      const [p,c,q,r] = await Promise.all([
        apiFetch<Summary>("/patients/summary"),
        apiFetch<ConflictSummary>("/conflicts/summary"),
        apiFetch<QueueResponse>(`/reviews/queue?${params}`),
        apiFetch<Reliability[]>("/reliability/"),
      ]);
      setSummary(p); setConflictSummary(c); setQueue(q.records || []);
      setReliability([...r].sort((a,b)=>b.source_reliability-a.source_reliability));
    } catch (e) { setError(e instanceof Error ? e.message : "Could not load data from API"); }
    finally { setLoading(false); }
  },[user,search,district,statusFilter]);

  useEffect(() => { void loadData(); },[loadData]);

  async function logout() {
    try { await apiFetch("/auth/logout",{method:"POST"}); } catch { /* clear local session regardless */ }
    clearSession(); router.replace("/login");
  }

  async function submitReview(event:FormEvent, status:"approved"|"rejected"|"escalated"|"flagged_for_review") {
    event.preventDefault();
    if (!selected) return;
    setActionBusy(true); setError("");
    try {
      await apiFetch("/reviews/overrides",{method:"POST",body:JSON.stringify({
        patient_id:String(selected.patient_id),field:String(selected.conflict_types || "record review"),source,chosen_value:value || "No value supplied",reason,status,notes,
      })});
      setSelected(null); setValue(""); setNotes(""); await loadData();
    } catch(e) { setError(e instanceof Error ? e.message : "Could not save review"); }
    finally { setActionBusy(false); }
  }

  const conflictRate = useMemo(() => conflictSummary?.patients_analysed ? (100*conflictSummary.patients_with_conflicts/conflictSummary.patients_analysed).toFixed(1) : "0.0",[conflictSummary]);
  if (!user) return <main className="loading-screen">Checking session…</main>;

  const canReview = user.role === "admin" || user.role === "reviewer";
  const cards = [
    ["TOTAL PATIENTS",summary?.total_patients,"Karnataka cohort","#3b82f6"],
    ["RESOLVED CONFLICTS",conflictSummary?.resolved_conflicts,"Recorded in audit log","#10b981"],
    ["PATIENTS WITH CONFLICTS",conflictSummary?.patients_with_conflicts,"At least one field disagreement","#f59e0b"],
    ["CONFLICT RATE",`${conflictRate}%`,"Of analysed patients","#ef4444"],
  ] as const;

  return <main className="app-shell">
    <aside className="sidebar"><div className="brand"><span className="brand-mark">H</span><div><b>HealthSync</b><small>KARNATAKA HUB</small></div></div>
      <p className="eyebrow">MAIN NAVIGATION</p><a className="nav-item active" href="#overview">▦　Dashboard</a><a className="nav-item" href="#queue">◉　Conflict review queue <span>{conflictSummary?.patients_with_conflicts ?? "—"}</span></a><a className="nav-item" href="#reliability">⬡　Source reliability</a><a className="nav-item" href="#audit">↻　Audit / overrides</a>{user.role === "admin" && <a className="nav-item" href="#admin">⚙　Admin controls</a>}
      <div className="side-bottom"><b>{user.name}</b><small>{user.role.toUpperCase()}</small><button className="secondary-button" onClick={logout}>Sign out</button></div>
    </aside>
    <section className="workspace"><header className="topbar"><h1>Supervisor Dashboard</h1><div className="user-chip">{user.name} · {user.role}</div><button className="secondary-button" onClick={logout}>Logout</button></header>
      <div className="content" id="overview">
        {error && <div className="error" role="alert">{error} <button className="link-button" onClick={()=>void loadData()}>Retry</button></div>}
        <section className="metrics">{cards.map(([label,val,sub,color])=><article className="metric" key={label}><div className="eyebrow">{label}</div><strong style={{color}}>{loading ? "…" : (val ?? "—")}</strong><p>{sub}</p></article>)}</section>
        <section className="metrics two"><article className="metric"><div className="eyebrow">HIGH-RISK PATIENTS</div><strong style={{color:"#ef4444"}}>{summary?.high_risk_patients ?? "—"}</strong><p>Predicted by the configured pipeline</p></article><article className="metric"><div className="eyebrow">NORMAL RISK</div><strong style={{color:"#10b981"}}>{summary?.normal_patients ?? "—"}</strong><p>No high-risk indicators in current model output</p></article></section>
        <section className="columns"><div id="queue"><div className="section-title"><div><h2>Conflict Review Queue</h2><p>{conflictSummary?.patients_with_conflicts ?? 0} cases · oldest/highest conflict count first</p></div><button className="secondary-button" onClick={()=>void loadData()}>Refresh</button></div>
          <div className="filters"><input aria-label="Search patients" placeholder="Search patient, ID, district, village…" value={search} onChange={e=>setSearch(e.target.value)}/><input aria-label="District filter" placeholder="District" value={district} onChange={e=>setDistrict(e.target.value)}/><select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="escalated">Escalated</option><option value="flagged_for_review">Flagged</option><option value="all">All statuses</option></select></div>
          <div className="queue-list">{loading ? <p className="muted">Loading queue…</p> : queue.length ? queue.map(row=><article className="queue-row" key={row.patient_id}><div><span className="patient-id">{row.patient_id}</span><span className={`status status-${row.review_status}`}>{String(row.review_status).replaceAll("_"," ")}</span><h3>{row.name || "Patient"}</h3><p>{row.district || "District unavailable"}{row.village ? ` · ${row.village}` : ""}</p><p><b>Fields:</b> {row.conflict_types || "Conflict details unavailable"}</p></div><div className="row-actions"><span>{row.num_conflicts ?? "—"} conflicts</span><button className="primary-button" onClick={()=>{setSelected(row);setValue("");}}>Review</button></div></article>) : <div className="empty">No cases match these filters.</div>}</div>
        </div><aside className="reliability" id="reliability" style={panel}><h2>Source Reliability</h2><p className="muted">Mean reliability scores from the API.</p>{reliability.map((item,index)=><div className="reliability-row" key={item.cadre}><div><span>#{index+1}　</span><b>{item.cadre}</b><strong>{(item.source_reliability*100).toFixed(1)}%</strong></div><div className="bar"><i style={{width:`${Math.max(0,Math.min(100,item.source_reliability*100))}%`}}/></div></div>)}{!reliability.length&&<p className="muted">No reliability data available.</p>}<h2 id="audit">Recent overrides</h2><p className="muted">Overrides are recorded by reviewer, timestamp, reason, and selected value in the API audit file.</p></aside></section>
      </div>
    </section>
    {selected && <div className="modal-backdrop" role="presentation" onClick={()=>setSelected(null)}><section className="review-modal" role="dialog" aria-modal="true" aria-labelledby="review-title" onClick={e=>e.stopPropagation()}><button className="close-button" onClick={()=>setSelected(null)} aria-label="Close">×</button><div className="eyebrow">PATIENT {selected.patient_id}</div><h2 id="review-title">Review conflict · {selected.name || "Patient"}</h2><p className="muted">{selected.district} {selected.village ? `· ${selected.village}` : ""}</p><div className="notice"><b>Detected fields:</b> {selected.conflict_types || "not provided"}<br/><b>Risk indicators:</b> {String(selected.predicted_high_risk ?? "Not included in queue response")}</div><form className="stack" onSubmit={e=>void submitReview(e,"approved")}><label>Choose source<input value={source} onChange={e=>setSource(e.target.value)} placeholder="ASHA / ANM / PHC / Anganwadi" required/></label><label>Selected/corrected value<input value={value} onChange={e=>setValue(e.target.value)} placeholder="Enter reviewed value" required/></label><label>Reason<select value={reason} onChange={e=>setReason(e.target.value)}><option>Source is more reliable</option><option>Data entry error</option><option>Missing or duplicate record</option><option>Patient changed over time</option><option>Clinician confirmation</option><option>False positive</option><option>Other</option></select></label><label>Reviewer notes<textarea value={notes} onChange={e=>setNotes(e.target.value)} rows={3}/></label><div className="modal-actions"><button className="primary-button" disabled={!canReview||actionBusy}>{actionBusy?"Saving…":"Approve override"}</button><button type="button" className="secondary-button" disabled={!canReview||actionBusy} onClick={e=>void submitReview(e as unknown as FormEvent,"rejected")}>Reject</button><button type="button" className="secondary-button" disabled={!canReview||actionBusy} onClick={e=>void submitReview(e as unknown as FormEvent,"escalated")}>Escalate</button></div>{!canReview&&<p className="muted">Your role has read-only access. Reviewer or admin permissions are required to make decisions.</p>}</form></section></div>}
  </main>;
}
