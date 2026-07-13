import React, { useEffect, useState, useCallback } from "react";
import api from "../api/client";

// SVG icons for pipeline stages — no emojis
const STAGE_ICONS = {
  dataset_generation:  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>,
  standardization:     <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>,
  blocking:            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>,
  entity_resolution:   <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>,
  conflict_detection:  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  reliability_scoring: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  bayesian_resolution: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
  risk_prediction:     <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
};

const STAGE_LABELS = {
  dataset_generation:  "Dataset Generation",
  standardization:     "Standardization",
  blocking:            "Blocking",
  entity_resolution:   "Entity Resolution",
  conflict_detection:  "Conflict Detection",
  reliability_scoring: "Reliability Scoring",
  bayesian_resolution: "Bayesian Resolution",
  risk_prediction:     "Risk Prediction",
};

const CONFLICT_LABELS = {
  haemoglobin_conflict:    "Haemoglobin",
  blood_pressure_conflict: "Blood Pressure",
  blood_sugar_conflict:    "Blood Sugar",
  anc_visit_conflict:      "ANC Visits",
  weight_conflict:         "Body Weight",
  fundal_height_conflict:  "Fundal Height",
};

function humanise(raw) {
  if (!raw || raw === "no_conflict") return null;
  return raw.split(",")
    .map(s => CONFLICT_LABELS[s.trim()] || s.trim().replace(/_/g, " ").replace(/conflict/gi, "").trim())
    .join(", ");
}

export default function Audit() {
  const [pipeline,  setPipeline]  = useState({});
  const [records,   setRecords]   = useState([]);
  const [total,     setTotal]     = useState(0);
  const [stats,     setStats]     = useState(null);
  const [districts, setDistricts] = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(false);

  const [search,   setSearch]   = useState("");
  const [district, setDistrict] = useState("");
  const [page,     setPage]     = useState(1);
  const LIMIT = 50;

  const fetchRecords = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search)   params.set("search",   search);
    if (district) params.set("district", district);
    params.set("page",  page);
    params.set("limit", LIMIT);

    api.get(`/audit/resolved?${params.toString()}`)
      .then(r => {
        setRecords(r.data.records || []);
        setTotal(r.data.total || 0);
        setLoading(false);
      })
      .catch(() => { setError(true); setLoading(false); });
  }, [search, district, page]);

  useEffect(() => {
    api.get("/audit/pipeline").then(r => setPipeline(r.data)).catch(() => {});
    api.get("/audit/stats").then(r => setStats(r.data)).catch(() => {});
    api.get("/conflicts/districts").then(r => setDistricts(r.data)).catch(() => {});
  }, []);

  useEffect(() => { fetchRecords(); }, [fetchRecords]);

  if (error) return (
    <div style={{ color: "#ef4444", padding: 60, textAlign: "center", fontSize: 14 }}>
      ⚠️ Failed to load audit data.
    </div>
  );

  const total_stages = Object.values(pipeline).length;
  const passed       = Object.values(pipeline).filter(Boolean).length;
  const totalPages   = Math.ceil(total / LIMIT);

  return (
    <div>
      {/* Pipeline health */}
      <div style={{
        background: "#0f1623", borderRadius: 14,
        border: "1px solid rgba(255,255,255,0.07)",
        padding: "20px 24px", marginBottom: 20,
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 16 }}>
          <div>
            <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1.5px", fontWeight: 600, marginBottom: 4 }}>
              PIPELINE HEALTH
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: passed === total_stages && total_stages > 0 ? "#10b981" : "#f59e0b" }}>
              {total_stages > 0 ? `${passed}/${total_stages} stages passing` : "Loading…"}
            </div>
          </div>
          {stats && (
            <div style={{ display: "flex", gap: 24, flexShrink: 0 }}>
              {[
                { label: "Total Resolved",   val: stats.total_resolved, color: "white" },
                { label: "Had Conflicts",    val: stats.with_conflicts, color: "#f59e0b" },
                { label: "Bayesian Applied", val: stats.auto_resolved,  color: "#60a5fa" },
              ].map(s => (
                <div key={s.label} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>
                    {s.val?.toLocaleString()}
                  </div>
                  <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1px", marginTop: 2 }}>{s.label}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Stage chips — SVG icons, no emojis */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {Object.entries(pipeline).map(([key, value]) => (
            <div key={key} style={{
              display: "flex", alignItems: "center", gap: 6,
              background: value ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)",
              border: `1px solid ${value ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)"}`,
              borderRadius: 8, padding: "6px 12px",
            }}>
              <span style={{ color: value ? "#10b981" : "#ef4444" }}>
                {STAGE_ICONS[key]}
              </span>
              <span style={{ fontSize: 11, color: value ? "#10b981" : "#ef4444", fontWeight: 600 }}>
                {STAGE_LABELS[key] || key.replaceAll("_", " ")}
              </span>
              {value
                ? <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>
                : <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              }
            </div>
          ))}
        </div>
      </div>

      {/* Resolved records table */}
      <div style={{
        background: "#0f1623", borderRadius: 14,
        border: "1px solid rgba(255,255,255,0.07)", overflow: "hidden",
      }}>
        <div style={{
          padding: "18px 24px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "white", margin: "0 0 4px" }}>
            Supervisor Resolution Log
            <span style={{ fontSize: 12, color: "#4b5563", fontWeight: 400, marginLeft: 8 }}>
              {total.toLocaleString()} total
            </span>
          </h3>
          <p style={{ fontSize: 12, color: "#4b5563", margin: 0 }}>
            These are the final values accepted by the system after Bayesian weighted resolution.
            Values from higher-reliability sources (PHC 97%, ANM 90%) carry more weight than lower-reliability ones (ASHA 65%).
          </p>
        </div>

        {/* Search + filter */}
        <div style={{
          padding: "14px 20px",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
          display: "flex", gap: 10,
        }}>
          <div style={{
            flex: 1, background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 8, padding: "9px 14px",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4b5563" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search by patient ID, name, district, or village…"
              style={{
                background: "transparent", border: "none", outline: "none",
                color: "#e2e8f0", fontSize: 13, width: "100%",
              }}
            />
            {search && (
              <button onClick={() => { setSearch(""); setPage(1); }}
                style={{ background: "transparent", border: "none", cursor: "pointer", color: "#4b5563" }}>✕</button>
            )}
          </div>
          <select
            value={district}
            onChange={e => { setDistrict(e.target.value); setPage(1); }}
            style={{
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 8, padding: "9px 12px",
              color: "#9ca3af", fontSize: 13, outline: "none", cursor: "pointer",
            }}
          >
            <option value="">All Districts</option>
            {districts.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        {/* Table header */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1.3fr 1fr 1.4fr 1fr 1fr 1.3fr",
          padding: "10px 20px",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
          fontSize: 10, color: "#374151", letterSpacing: "1.5px", fontWeight: 600,
        }}>
          <span>PATIENT ID</span>
          <span>NAME</span>
          <span>DISTRICT</span>
          <span>CONFLICT TYPE</span>
          <span>METHOD</span>
          <span>RESOLVED BY</span>
          <span>TIMESTAMP</span>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: "center", color: "#4b5563", fontSize: 13 }}>Loading…</div>
        ) : records.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "#4b5563", fontSize: 13 }}>
            No records match your search.
          </div>
        ) : (
          records.map((r, i) => {
            const conflictFields = humanise(r.conflict_types);
            const wasConflicted  = !!conflictFields;
            return (
              <div key={r.patient_id} style={{
                display: "grid",
                gridTemplateColumns: "1fr 1.3fr 1fr 1.4fr 1fr 1fr 1.3fr",
                padding: "12px 20px",
                borderBottom: i < records.length - 1 ? "1px solid rgba(255,255,255,0.03)" : "none",
                background: i % 2 === 0 ? "#0f1623" : "rgba(255,255,255,0.012)",
                alignItems: "center",
              }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.025)"}
                onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? "#0f1623" : "rgba(255,255,255,0.012)"}
              >
                <span style={{ fontFamily: "monospace", color: "#9ca3af", fontSize: 12 }}>
  {r.patient_id}
</span>

<span style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 500 }}>
  {r.name}
</span>

<span style={{ color: "#6b7280", fontSize: 12 }}>
  {r.district}
</span>

<span style={{ color: "#f59e0b", fontSize: 12 }}>
  {humanise(r.conflict_types)}
</span>

<span style={{ color: "#60a5fa", fontSize: 12, fontWeight: 600 }}>
  {r.resolution_method}
</span>

<span style={{ color: "#e2e8f0", fontSize: 12 }}>
  {r.resolved_by}
</span>

<span style={{ color: "#9ca3af", fontSize: 12 }}>
  {r.resolved_at}
</span>
              </div>
            );
          })
        )}

        {totalPages > 1 && (
          <div style={{
            padding: "14px 20px",
            borderTop: "1px solid rgba(255,255,255,0.05)",
            display: "flex", justifyContent: "center", gap: 8, alignItems: "center",
          }}>
            <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
              style={{
                background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 6, padding: "6px 14px",
                color: page === 1 ? "#374151" : "#9ca3af",
                fontSize: 12, cursor: page === 1 ? "not-allowed" : "pointer",
              }}>← Prev</button>
            <span style={{ fontSize: 13, color: "#4b5563" }}>
              Page {page} of {totalPages} · {total.toLocaleString()} records
            </span>
            <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}
              style={{
                background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 6, padding: "6px 14px",
                color: page === totalPages ? "#374151" : "#9ca3af",
                fontSize: 12, cursor: page === totalPages ? "not-allowed" : "pointer",
              }}>Next →</button>
          </div>
        )}
      </div>
    </div>
  );
}