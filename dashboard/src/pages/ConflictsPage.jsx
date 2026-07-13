import React, { useEffect, useState, useCallback } from "react";
import api from "../api/client";

const CONFLICT_LABELS = {
  haemoglobin_conflict:    "Haemoglobin Level",
  blood_pressure_conflict: "Blood Pressure",
  blood_sugar_conflict:    "Blood Sugar (Fasting)",
  anc_visit_conflict:      "ANC Visits",
  weight_conflict:         "Body Weight",
  fundal_height_conflict:  "Fundal Height",
};

function humaniseConflicts(raw) {
  if (!raw || raw === "no_conflict") return "No Conflict";
  return raw.split(",")
    .map(s => CONFLICT_LABELS[s.trim()] || s.trim().replace(/_/g, " ").replace(/conflict/gi, "").trim())
    .join(", ");
}

function ConflictModal({ item, onClose }) {
  const [detail, setDetail]   = useState(null);
  const [loading, setLoading] = useState(true);
  const handleResolve = async () => {
  try {
    await api.post(
      `/conflicts/resolve/${item.patient_id}`,
      {
        resolved_by: "District Health Officer"
      }
    );

    alert("Conflict resolved successfully");

window.location.reload();
  } catch (err) {
    console.error(err);
    alert("Failed to resolve conflict");
  }
};

  useEffect(() => {
    if (!item) return;
    setLoading(true);
    api.get(`/conflicts/${item.patient_id}`)
      .then(r => { setDetail(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [item?.patient_id]);

  if (!item) return null;
  const allFields = item.conflict_types && item.conflict_types !== "no_conflict"
    ? item.conflict_types.split(",").map(f => CONFLICT_LABELS[f.trim()] || f.trim().replace(/_/g, " ").replace(/conflict/gi, "").trim())
    : [];

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0,
      background: "rgba(0,0,0,0.7)", backdropFilter: "blur(4px)",
      zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: 20,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#0f1623", borderRadius: 16,
        border: "1px solid rgba(255,255,255,0.1)",
        width: "100%", maxWidth: 720, maxHeight: "85vh", overflowY: "auto", padding: 32,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
          <div>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <span style={{
                background: "rgba(255,255,255,0.08)", color: "#9ca3af",
                fontSize: 12, fontWeight: 600, padding: "3px 10px", borderRadius: 6,
              }}>{item.num_conflicts} Conflict{item.num_conflicts > 1 ? "s" : ""}</span>
              <span style={{
                background: item.num_conflicts >= 3 ? "#ef4444" : item.num_conflicts === 2 ? "#f59e0b" : "#10b981",
                color: "white", fontSize: 12, fontWeight: 700, padding: "3px 10px", borderRadius: 6,
              }}>{item.num_conflicts >= 3 ? "HIGH" : item.num_conflicts === 2 ? "MEDIUM" : "LOW"}</span>
            </div>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: "white", margin: "0 0 4px" }}>{item.name}</h2>
            <p style={{ fontSize: 13, color: "#6b7280", margin: 0 }}>
              <span style={{ fontFamily: "monospace", color: "#9ca3af" }}>{item.patient_id}</span>
              {" · "}{item.district}{" · "}{item.village}
            </p>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", cursor: "pointer", color: "#4b5563" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {allFields.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "12px 0 20px" }}>
            {allFields.map(f => (
              <span key={f} style={{
                background: "rgba(239,68,68,0.1)", color: "#fca5a5",
                fontSize: 11, fontWeight: 600,
                padding: "3px 10px", borderRadius: 20, border: "1px solid rgba(239,68,68,0.2)",
              }}>{f}</span>
            ))}
          </div>
        )}

        {loading ? (
          <div style={{ color: "#4b5563", textAlign: "center", padding: "32px 0" }}>Loading source data…</div>
        ) : detail?.sources ? (
          <>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#9ca3af", marginBottom: 10 }}>
              Values recorded by each cadre:
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 10, marginBottom: 20 }}>
              {detail.sources.map(s => (
                <div key={s.cadre} style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 10, padding: 16,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10, alignItems: "center" }}>
                    <span style={{ fontSize: 13, fontWeight: 700, color: "white" }}>{s.cadre}</span>
                    <span style={{
                      background: "#1d4ed8", color: "#93c5fd",
                      fontSize: 10, fontWeight: 600,
                      padding: "2px 8px", borderRadius: 20,
                    }}>Reliability: {(s.reliability * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {[
  { label: "Haemoglobin", val: `${s.haemoglobin} g/dL` },
  { label: "Systolic BP", val: `${s.blood_pressure} mmHg` },
  { label: "Blood Sugar", val: `${s.blood_sugar} mg/dL` },
  { label: "ANC Visits", val: s.anc_visits },
  { label: "Weight", val: `${s.weight} kg` },
  { label: "Fundal Height", val: `${s.fundal_height} cm` },
].map(({ label, val }) => (
                      <div key={label} style={{ display: "flex", justifyContent: "space-between" }}>
                        <span style={{ fontSize: 11, color: "#4b5563" }}>{label}</span>
                        <span style={{ fontSize: 12, fontWeight: 600, color: "white" }}>{val}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Bayesian resolved */}
            <div style={{
              background: "rgba(59,130,246,0.06)",
              border: "1px solid rgba(59,130,246,0.2)",
              borderRadius: 10, padding: 16, marginBottom: 20,
            }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#60a5fa", marginBottom: 10 }}>
                ✦ Bayesian Resolved Values
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
                {[
  { label: "Haemoglobin", val: `${detail.resolved_values.haemoglobin} g/dL` },
  { label: "Systolic BP", val: `${detail.resolved_values.blood_pressure} mmHg` },
  { label: "Blood Sugar", val: `${detail.resolved_values.blood_sugar} mg/dL` },
  { label: "ANC Visits", val: detail.resolved_values.anc_visits },
  { label: "Weight", val: `${detail.resolved_values.weight} kg` },
  { label: "Fundal Height", val: `${detail.resolved_values.fundal_height} cm` },
].map(({ label, val }) => (
                  <div key={label} style={{ background: "rgba(255,255,255,0.04)", borderRadius: 8, padding: 12 }}>
                    <div style={{ fontSize: 10, color: "#4b5563", marginBottom: 4 }}>{label}</div>
                    <div style={{ fontSize: 15, fontWeight: 700, color: "white" }}>{val}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk */}
            <div style={{
              background: detail.predicted_high_risk ? "rgba(239,68,68,0.08)" : "rgba(16,185,129,0.08)",
              border: `1px solid ${detail.predicted_high_risk ? "rgba(239,68,68,0.2)" : "rgba(16,185,129,0.2)"}`,
              borderRadius: 10, padding: 14,
              display: "flex", justifyContent: "space-between", alignItems: "center",
            }}>
              <div>
                <div style={{ fontSize: 11, color: "#4b5563", marginBottom: 4 }}>MATERNAL RISK</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: detail.predicted_high_risk ? "#ef4444" : "#10b981" }}>
                  {detail.predicted_high_risk ? "⚠ High Risk" : "✓ Normal Risk"}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 11, color: "#4b5563", marginBottom: 4 }}>RISK SCORE</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: "white" }}>{detail.risk_score}</div>
              </div>
            </div>
            <div
  style={{
    display: "flex",
    justifyContent: "flex-end",
    marginTop: 20,
  }}
>
  <button
    onClick={handleResolve}
    style={{
      background: "#2563eb",
      color: "white",
      border: "none",
      borderRadius: 8,
      padding: "10px 18px",
      fontSize: 13,
      fontWeight: 600,
      cursor: "pointer",
    }}
  >
    Accept Bayesian Resolution
  </button>
</div>
          </>
        ) : (
          <div style={{ color: "#ef4444", fontSize: 13 }}>Could not load source data.</div>
        )}
      </div>
    </div>
  );
}

export default function Conflicts() {
  const [records,    setRecords]    = useState([]);
  const [total,      setTotal]      = useState(0);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(false);
  const [selected,   setSelected]   = useState(null);
  const [showFilter, setShowFilter] = useState(false);
  const [districts,  setDistricts]  = useState([]);
  const [conflictTypes, setConflictTypes] = useState([]);

  // Filter state
  const [search,       setSearch]       = useState("");
  const [district,     setDistrict]     = useState("");
  const [conflictType, setConflictType] = useState("");
  const [hasConflict,  setHasConflict]  = useState("true"); // default: show conflicts only
  const [page,         setPage]         = useState(1);
  const LIMIT = 50;

  const fetchData = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search)       params.set("search",       search);
    if (district)     params.set("district",     district);
    if (conflictType) params.set("conflict_type", conflictType);
    if (hasConflict !== "") params.set("has_conflict", hasConflict);
    params.set("page",  page);
    params.set("limit", LIMIT);

    api.get(`/conflicts/?${params.toString()}`)
      .then(r => {
        setRecords(r.data.records || []);
        setTotal(r.data.total || 0);
        setLoading(false);
      })
      .catch(() => { setError(true); setLoading(false); });
  }, [search, district, conflictType, hasConflict, page]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    api.get("/conflicts/districts").then(r => setDistricts(r.data)).catch(() => {});
    api.get("/conflicts/conflict-types").then(r => setConflictTypes(r.data)).catch(() => {});
  }, []);
  useEffect(() => {
  const targetPatient =
    localStorage.getItem("selectedConflictPatient");

  if (!targetPatient) return;

  const patient = records.find(
    r => r.patient_id === targetPatient
  );

  if (patient) {
    setSelected(patient);
    localStorage.removeItem(
      "selectedConflictPatient"
    );
  }
}, [records]);
  const selectStyle = {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 8, padding: "8px 12px",
    color: "#9ca3af", fontSize: 13, cursor: "pointer", outline: "none",
    width: "100%",
  };

  if (error) return (
    <div style={{ color: "#ef4444", padding: 60, textAlign: "center", fontSize: 14 }}>
      ⚠️ Failed to load conflicts. Is the backend running?
    </div>
  );

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <>
      {selected && <ConflictModal item={selected} onClose={() => setSelected(null)} />}

      <div>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 20 }}>
          <div>
            <p style={{ fontSize: 12, color: "#4b5563", margin: "0 0 6px" }}>
              Multi-source data conflicts · Karnataka maternal records
            </p>
            <div style={{ fontSize: 13, color: "#9ca3af" }}>
              Showing <strong style={{ color: "white" }}>{records.length}</strong> of{" "}
              <strong style={{ color: "white" }}>{total}</strong> records
            </div>
          </div>
          <button
            onClick={() => setShowFilter(!showFilter)}
            style={{
              background: showFilter ? "rgba(59,130,246,0.15)" : "rgba(255,255,255,0.06)",
              border: `1px solid ${showFilter ? "rgba(59,130,246,0.4)" : "rgba(255,255,255,0.1)"}`,
              borderRadius: 8, padding: "8px 14px",
              color: showFilter ? "#60a5fa" : "#9ca3af",
              fontSize: 13, fontWeight: 600, cursor: "pointer",
              display: "flex", alignItems: "center", gap: 6,
            }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
            </svg>
            Filters
          </button>
        </div>

        {/* Search bar */}
        <div style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 8, padding: "10px 16px",
          display: "flex", alignItems: "center", gap: 10,
          marginBottom: 12,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4b5563" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by patient name, ID (W00001), district, or village…"
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

        {/* Filter panel */}
        {showFilter && (
          <div style={{
            background: "#0f1623",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 10, padding: 20, marginBottom: 16,
          }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14 }}>
              {/* District */}
              <div>
                <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1px", fontWeight: 600, marginBottom: 6 }}>DISTRICT</div>
                <select value={district} onChange={e => { setDistrict(e.target.value); setPage(1); }} style={selectStyle}>
                  <option value="">All Districts</option>
                  {districts.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>

              {/* Conflict type */}
              <div>
                <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1px", fontWeight: 600, marginBottom: 6 }}>CONFLICT TYPE</div>
                <select value={conflictType} onChange={e => { setConflictType(e.target.value); setPage(1); }} style={selectStyle}>
                  <option value="">All Types</option>
                  {conflictTypes.map(c => <option key={c.key} value={c.key}>{c.label}</option>)}
                </select>
              </div>

              {/* Has conflict */}
              <div>
                <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1px", fontWeight: 600, marginBottom: 6 }}>RECORD STATUS</div>
                <select value={hasConflict} onChange={e => { setHasConflict(e.target.value); setPage(1); }} style={selectStyle}>
                  <option value="">All Records</option>
                  <option value="true">With Conflicts Only</option>
                  <option value="false">Clean Records Only</option>
                </select>
              </div>
            </div>

            <div style={{ marginTop: 12 }}>
              <button
                onClick={() => { setSearch(""); setDistrict(""); setConflictType(""); setHasConflict("true"); setPage(1); }}
                style={{
                  background: "transparent", border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 6, padding: "6px 14px",
                  color: "#6b7280", fontSize: 12, cursor: "pointer",
                }}
              >
                Reset Filters
              </button>
            </div>
          </div>
        )}

        {/* Table */}
        <div style={{
          background: "#0f1623", borderRadius: 14,
          border: "1px solid rgba(255,255,255,0.07)", overflow: "hidden",
        }}>
          <div style={{
            display: "grid", gridTemplateColumns: "1.2fr 1.5fr 1fr 2fr 1fr 0.8fr",
            padding: "12px 20px", borderBottom: "1px solid rgba(255,255,255,0.06)",
            fontSize: 10, color: "#374151", letterSpacing: "1.5px", fontWeight: 600,
          }}>
            <span>PATIENT ID</span>
            <span>NAME</span>
            <span>DISTRICT</span>
            <span>CONFLICTS</span>
            <span>STATUS</span>
            <span>ACTION</span>
          </div>

          {loading ? (
            <div style={{ padding: 40, textAlign: "center", color: "#4b5563", fontSize: 13 }}>Loading…</div>
          ) : records.length === 0 ? (
            <div style={{ padding: 40, textAlign: "center", color: "#4b5563", fontSize: 13 }}>
              No records match your filters.
            </div>
          ) : (
            records.map((item, i) => {
              const isConflict = item.has_conflict;
              return (
                <div key={item.patient_id} style={{
                  display: "grid", gridTemplateColumns: "1.2fr 1.5fr 1fr 2fr 1fr 0.8fr",
                  padding: "13px 20px",
                  borderBottom: i < records.length - 1 ? "1px solid rgba(255,255,255,0.03)" : "none",
                  background: i % 2 === 0 ? "#0f1623" : "rgba(255,255,255,0.012)",
                  alignItems: "center",
                }}
                  onMouseEnter={e => e.currentTarget.style.background = "rgba(59,130,246,0.05)"}
                  onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? "#0f1623" : "rgba(255,255,255,0.012)"}
                >
                  <span style={{ color: "#9ca3af", fontSize: 12, fontFamily: "monospace" }}>{item.patient_id}</span>
                  <span style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 500 }}>{item.name}</span>
                  <span style={{ color: "#6b7280", fontSize: 12 }}>{item.district}</span>
                  <span style={{ color: "#6b7280", fontSize: 12 }}>
                    {item.conflict_label || humaniseConflicts(item.conflict_types)}
                  </span>
                  <span>
                    {isConflict
                      ? <span style={{ color: "#f59e0b", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#f59e0b", display: "inline-block" }} />
                          Review
                        </span>
                      : <span style={{ color: "#10b981", fontSize: 12, display: "flex", alignItems: "center", gap: 4 }}>
                          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", display: "inline-block" }} />
                          Clean
                        </span>
                    }
                  </span>
                  <span>
                    {isConflict && (
                      <button
                        onClick={() => setSelected(item)}
                        style={{
                          background: "rgba(29,78,216,0.2)", color: "#60a5fa",
                          border: "1px solid rgba(59,130,246,0.3)",
                          borderRadius: 6, padding: "5px 12px",
                          fontSize: 12, fontWeight: 600, cursor: "pointer",
                        }}
                      >
                        Resolve
                      </button>
                    )}
                  </span>
                </div>
              );
            })
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 16, alignItems: "center" }}>
            <button
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              style={{
                background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 6, padding: "6px 14px", color: page === 1 ? "#374151" : "#9ca3af",
                fontSize: 12, cursor: page === 1 ? "not-allowed" : "pointer",
              }}
            >← Prev</button>
            <span style={{ fontSize: 13, color: "#4b5563" }}>
              Page {page} of {totalPages} · {total} total
            </span>
            <button
              disabled={page === totalPages}
              onClick={() => setPage(p => p + 1)}
              style={{
                background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 6, padding: "6px 14px", color: page === totalPages ? "#374151" : "#9ca3af",
                fontSize: 12, cursor: page === totalPages ? "not-allowed" : "pointer",
              }}
            >Next →</button>
          </div>
        )}
      </div>
    </>
  );
}