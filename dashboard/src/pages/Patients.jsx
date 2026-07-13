import React, { useEffect, useState, useCallback } from "react";
import api from "../api/client";

const RISK_REASONS = {
  severe_anaemia:      "Severe Anaemia",
  hypertension_risk:   "Hypertension Risk",
  diabetes_risk:       "Diabetes Risk",
  low_weight_risk:     "Low Weight",
  fundal_height_risk:  "Fundal Height",
  poor_anc_coverage:   "Poor ANC Coverage",
  none:                "—",
};

function RiskBadge({ isHighRisk, score }) {
  if (isHighRisk) {
    return (
      <span style={{
        background: "rgba(239,68,68,0.15)", color: "#fca5a5",
        border: "1px solid rgba(239,68,68,0.3)",
        fontSize: 10, fontWeight: 700,
        padding: "3px 9px", borderRadius: 20,
        display: "inline-flex", alignItems: "center", gap: 4,
      }}>
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#ef4444", display: "inline-block" }} />
        HIGH · {score}
      </span>
    );
  }
  return (
    <span style={{
      background: "rgba(16,185,129,0.1)", color: "#6ee7b7",
      border: "1px solid rgba(16,185,129,0.2)",
      fontSize: 10, fontWeight: 700,
      padding: "3px 9px", borderRadius: 20,
      display: "inline-flex", alignItems: "center", gap: 4,
    }}>
      <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#10b981", display: "inline-block" }} />
      NORMAL · {score}
    </span>
  );
}

const selectStyle = {
  background: "rgba(255,255,255,0.04)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8, padding: "9px 12px",
  color: "#9ca3af", fontSize: 13, outline: "none", cursor: "pointer",
};

export default function Patients() {
  const [records,   setRecords]   = useState([]);
  const [total,     setTotal]     = useState(0);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(false);
  const [districts, setDistricts] = useState([]);

  const [search,    setSearch]    = useState("");
  const [district,  setDistrict]  = useState("");
  const [riskLevel, setRiskLevel] = useState("");   // "" | "high" | "normal"
  const [page,      setPage]      = useState(1);
  const LIMIT = 50;

  const fetchData = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search)    params.set("search",     search);
    if (district)  params.set("district",   district);
    if (riskLevel) params.set("risk_level", riskLevel);
    params.set("page",  page);
    params.set("limit", LIMIT);

    api.get(`/patients/?${params.toString()}`)
      .then(r => {
        setRecords(r.data.records || []);
        setTotal(r.data.total || 0);
        setLoading(false);
      })
      .catch(() => { setError(true); setLoading(false); });
  }, [search, district, riskLevel, page]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    api.get("/patients/districts").then(r => setDistricts(r.data)).catch(() => {});
  }, []);

  if (error) return (
    <div style={{ color: "#ef4444", padding: 60, textAlign: "center", fontSize: 14 }}>
      ⚠️ Failed to load patient data.
    </div>
  );

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div>
      {/* Summary bar */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        {[
          { label: "All Patients",   val: total, active: riskLevel === "",       key: ""       },
          { label: "High Risk",      val: null,  active: riskLevel === "high",   key: "high"   },
          { label: "Normal Risk",    val: null,  active: riskLevel === "normal", key: "normal" },
        ].map(f => (
          <button
            key={f.key}
            onClick={() => { setRiskLevel(f.key); setPage(1); }}
            style={{
              background: f.active ? "rgba(59,130,246,0.15)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${f.active ? "rgba(59,130,246,0.4)" : "rgba(255,255,255,0.08)"}`,
              borderRadius: 8, padding: "8px 16px",
              color: f.active ? "#60a5fa" : "#6b7280",
              fontSize: 13, fontWeight: f.active ? 600 : 400,
              cursor: "pointer",
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Search + filters */}
      <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
        <div style={{
          flex: 1,
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 8, padding: "9px 14px",
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4b5563" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by name, patient ID (W00001), district, or village…"
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

        <select value={district} onChange={e => { setDistrict(e.target.value); setPage(1); }} style={selectStyle}>
          <option value="">All Districts</option>
          {districts.map(d => <option key={d} value={d}>{d}</option>)}
        </select>

        <select value={riskLevel} onChange={e => { setRiskLevel(e.target.value); setPage(1); }} style={selectStyle}>
          <option value="">All Risk Levels</option>
          <option value="high">High Risk Only</option>
          <option value="normal">Normal Risk Only</option>
        </select>
      </div>

      {/* Result count */}
      <div style={{ fontSize: 13, color: "#4b5563", marginBottom: 12 }}>
        Showing <span style={{ color: "#9ca3af" }}>{records.length}</span> of{" "}
        <span style={{ color: "white", fontWeight: 600 }}>{total.toLocaleString()}</span> patients
      </div>

      {/* Table */}
      <div style={{
        background: "#0f1623", borderRadius: 14,
        border: "1px solid rgba(255,255,255,0.07)", overflow: "hidden",
      }}>
        {/* Header */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1.5fr 1fr 1fr 1fr 1fr 1.5fr",
          padding: "11px 20px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          fontSize: 10, color: "#374151", letterSpacing: "1.5px", fontWeight: 600,
        }}>
          <span>PATIENT ID</span>
          <span>NAME</span>
          <span>DISTRICT</span>
          <span>HAEMOGLOBIN</span>
          <span>SYSTOLIC BP</span>
          <span>RISK</span>
          <span>RISK REASON</span>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: "center", color: "#4b5563", fontSize: 13 }}>Loading…</div>
        ) : records.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "#4b5563", fontSize: 13 }}>
            No patients match your filters.
          </div>
        ) : (
          records.map((r, i) => {
            const reason = r.true_high_risk_reason && r.true_high_risk_reason !== "none"
              ? (RISK_REASONS[r.true_high_risk_reason] || r.true_high_risk_reason.replace(/_/g, " "))
              : "—";

            return (
              <div key={r.patient_id} style={{
                display: "grid",
                gridTemplateColumns: "1fr 1.5fr 1fr 1fr 1fr 1fr 1.5fr",
                padding: "12px 20px",
                borderBottom: i < records.length - 1 ? "1px solid rgba(255,255,255,0.03)" : "none",
                background: i % 2 === 0 ? "#0f1623" : "rgba(255,255,255,0.012)",
                alignItems: "center",
              }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(59,130,246,0.04)"}
                onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? "#0f1623" : "rgba(255,255,255,0.012)"}
              >
                <span style={{ fontFamily: "monospace", color: "#9ca3af", fontSize: 12 }}>
                  {r.patient_id}
                </span>
                <span style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 500 }}>
                  {r.name || "—"}
                </span>
                <span style={{ color: "#6b7280", fontSize: 12 }}>{r.district}</span>
                <span style={{ color: "white", fontSize: 13, fontWeight: 600 }}>
                  {r.haemoglobin_gdl != null ? `${Number(r.haemoglobin_gdl).toFixed(2)} g/dL` : "—"}
                </span>
                <span style={{ color: "white", fontSize: 13, fontWeight: 600 }}>
                  {r.systolic_bp != null ? `${Number(r.systolic_bp).toFixed(1)} mmHg` : "—"}
                </span>
                <span>
                  <RiskBadge isHighRisk={r.predicted_high_risk === 1} score={r.maternal_risk_score} />
                </span>
                <span style={{ color: "#6b7280", fontSize: 12 }}>{reason}</span>
              </div>
            );
          })
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 16, alignItems: "center" }}>
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
            style={{
              background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 6, padding: "6px 14px",
              color: page === 1 ? "#374151" : "#9ca3af",
              fontSize: 12, cursor: page === 1 ? "not-allowed" : "pointer",
            }}>← Prev</button>
          <span style={{ fontSize: 13, color: "#4b5563" }}>
            Page {page} of {totalPages} · {total.toLocaleString()} total
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
  );
}