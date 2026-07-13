import React, { useEffect, useState } from "react";
import api from "../api/client";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";

const card = {
  background: "#0f1623",
  borderRadius: 12,
  border: "1px solid rgba(255,255,255,0.07)",
  color: "white",
};

function KpiCard({ label, value, sub, color }) {
  return (
    <div style={{ ...card, padding: 24 }}>
      <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1.5px", marginBottom: 12, fontWeight: 600 }}>
        {label}
      </div>
      <div style={{ fontSize: 36, fontWeight: 800, color: color || "white", lineHeight: 1, marginBottom: 8 }}>
        {value ?? <span style={{ fontSize: 20, color: "#1f2937" }}>—</span>}
      </div>
      {sub && <div style={{ fontSize: 12, color: "#4b5563" }}>{sub}</div>}
    </div>
  );
}

// Maps raw conflict_types string to a single short human label
const CONFLICT_LABELS = {
  haemoglobin_conflict:    "Haemoglobin Level",
  blood_pressure_conflict: "Blood Pressure",
  blood_sugar_conflict:    "Blood Sugar",
  anc_visit_conflict:      "ANC Visits",
  weight_conflict:         "Body Weight",
  fundal_height_conflict:  "Fundal Height",
};

function primaryConflict(types) {
  if (!types || types === "no_conflict") return "No Conflict";
  const first = types.split(",")[0].trim();
  return CONFLICT_LABELS[first] || first.replace(/_/g, " ").replace(/\bconflict\b/gi, "").trim();
}

function ConflictCard({ item, index, onClick }) {
  const priority = item.num_conflicts >= 3 ? "HIGH" : item.num_conflicts === 2 ? "MEDIUM" : "LOW";
  const priorityColor = { HIGH: "#ef4444", MEDIUM: "#f59e0b", LOW: "#10b981" }[priority];

  return (
    <div
      onClick={() => onClick(item)}
      style={{
        background: "#0f1623",
        border: "1px solid rgba(255,255,255,0.07)",
        borderRadius: 12, padding: 20,
        cursor: "pointer",
        transition: "border-color 0.2s, transform 0.15s",
        width: "100%",
      }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(59,130,246,0.4)"; e.currentTarget.style.transform = "translateY(-2px)"; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)"; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span style={{ fontSize: 12, color: "#4b5563", fontWeight: 600 }}>{item.patient_id}</span>
          <span style={{
            background: priorityColor, color: "white",
            fontSize: 10, fontWeight: 700,
            padding: "2px 8px", borderRadius: 4,
          }}>{priority}</span>
        </div>
        <span style={{ fontSize: 11, color: "#4b5563" }}>{item.num_conflicts} field{item.num_conflicts > 1 ? "s" : ""}</span>
      </div>

      <div style={{ fontSize: 15, fontWeight: 700, color: "white", marginBottom: 4 }}>{item.name}</div>
      <div style={{ fontSize: 12, color: "#4b5563", marginBottom: 12 }}>
        {item.district} · {item.village}
      </div>

      <div style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.06)",
        borderRadius: 8, padding: 10,
      }}>
        <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1px", marginBottom: 4 }}>CONFLICTING FIELDS</div>
        <div style={{ fontSize: 13, fontWeight: 600, color: "white" }}>
          {primaryConflict(item.conflict_types)}
          {item.num_conflicts > 1 && (
            <span style={{ fontSize: 11, color: "#4b5563", fontWeight: 400 }}>
              {" "}+{item.num_conflicts - 1} more
            </span>
          )}
        </div>
        <div style={{ fontSize: 11, color: "#4b5563", marginTop: 3 }}>
          Across ASHA · ANM · PHC · Anganwadi
        </div>
      </div>
    </div>
  );
}

/* ── Conflict Detail Modal — calls real /conflicts/{patient_id} ── */
function ConflictModal({ item, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!item) return;
    api.get(`/conflicts/${item.patient_id}`)
      .then(r => { setDetail(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [item]);

  if (!item) return null;

  const allFields = item.conflict_types && item.conflict_types !== "no_conflict"
    ? item.conflict_types.split(",").map(f => {
        const key = f.trim();
        return CONFLICT_LABELS[key] || key.replace(/_/g, " ").replace(/conflict/gi, "").trim();
      })
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
        width: "100%", maxWidth: 720,
        maxHeight: "85vh", overflowY: "auto", padding: 32,
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
          <div>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <span style={{
                background: "rgba(255,255,255,0.08)", color: "#9ca3af",
                fontSize: 12, fontWeight: 600, padding: "3px 10px", borderRadius: 6,
              }}>
                {item.num_conflicts} Conflict{item.num_conflicts > 1 ? "s" : ""}
              </span>
              <span style={{
                background: item.num_conflicts >= 3 ? "#ef4444" : item.num_conflicts === 2 ? "#f59e0b" : "#10b981",
                color: "white", fontSize: 12, fontWeight: 700, padding: "3px 10px", borderRadius: 6,
              }}>
                {item.num_conflicts >= 3 ? "HIGH" : item.num_conflicts === 2 ? "MEDIUM" : "LOW"}
              </span>
            </div>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: "white", margin: "0 0 4px" }}>
              {item.name}
            </h2>
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

        {/* Conflicting fields list */}
        {allFields.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20, marginTop: 12 }}>
            {allFields.map(f => (
              <span key={f} style={{
                background: "rgba(239,68,68,0.1)", color: "#fca5a5",
                fontSize: 11, fontWeight: 600,
                padding: "3px 10px", borderRadius: 20, border: "1px solid rgba(239,68,68,0.2)",
              }}>{f}</span>
            ))}
          </div>
        )}

        {/* Source values from real backend */}
        {loading ? (
          <div style={{ color: "#4b5563", textAlign: "center", padding: "24px 0" }}>Loading source data…</div>
        ) : detail?.sources ? (
          <>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#9ca3af", marginBottom: 10 }}>
              Values reported by each source cadre:
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10, marginBottom: 20 }}>
              {detail.sources.map(s => (
                <div key={s.cadre} style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 10, padding: 16,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: "white" }}>{s.cadre}</span>
                    <span style={{
                      background: "#1d4ed8", color: "#93c5fd",
                      fontSize: 10, fontWeight: 600,
                      padding: "2px 8px", borderRadius: 20,
                    }}>
                      Reliability: {(s.reliability * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                    {[
                      { label: "Haemoglobin", val: `${s.haemoglobin} g/dL` },
                      { label: "Systolic BP",  val: `${s.blood_pressure} mmHg` },
                      { label: "Blood Sugar",  val: `${s.blood_sugar} mg/dL` },
                    ].map(({ label, val }) => (
                      <div key={label}>
                        <div style={{ fontSize: 10, color: "#4b5563", marginBottom: 2 }}>{label}</div>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "white" }}>{val}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Bayesian resolved values */}
            <div style={{
              background: "rgba(59,130,246,0.06)",
              border: "1px solid rgba(59,130,246,0.2)",
              borderRadius: 10, padding: 16, marginBottom: 20,
            }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#60a5fa", marginBottom: 10 }}>
                ✦ Bayesian Resolved Values (weighted by source reliability)
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                {[
                  { label: "Haemoglobin",  val: `${detail.resolved_values.haemoglobin} g/dL` },
                  { label: "Systolic BP",   val: `${detail.resolved_values.blood_pressure} mmHg` },
                  { label: "Blood Sugar",   val: `${detail.resolved_values.blood_sugar} mg/dL` },
                ].map(({ label, val }) => (
                  <div key={label} style={{
                    background: "rgba(255,255,255,0.04)", borderRadius: 8, padding: 12,
                  }}>
                    <div style={{ fontSize: 10, color: "#4b5563", marginBottom: 4 }}>{label}</div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: "white" }}>{val}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk */}
            <div style={{
              background: detail.predicted_high_risk ? "rgba(239,68,68,0.08)" : "rgba(16,185,129,0.08)",
              border: `1px solid ${detail.predicted_high_risk ? "rgba(239,68,68,0.2)" : "rgba(16,185,129,0.2)"}`,
              borderRadius: 10, padding: 14, marginBottom: 20,
              display: "flex", justifyContent: "space-between", alignItems: "center",
            }}>
              <div
  style={{
    display: "flex",
    justifyContent: "flex-end",
    marginTop: 20,
  }}
>
  <button
  onClick={() => {
    localStorage.setItem(
      "selectedConflictPatient",
      item.patient_id
    );

    setPage("conflicts");
  }}
>
  Open in Conflict Queue
</button>
</div>
              <div>
                <div style={{ fontSize: 11, color: "#4b5563", marginBottom: 4 }}>MATERNAL RISK PREDICTION</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: detail.predicted_high_risk ? "#ef4444" : "#10b981" }}>
                  {detail.predicted_high_risk ? "⚠ High Risk" : "✓ Normal Risk"}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 11, color: "#4b5563", marginBottom: 4 }}>RISK SCORE</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: "white" }}>{detail.risk_score}</div>
              </div>
            </div>

            {/* What supervisor should do */}
            <div style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 10, padding: 14,
            }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#9ca3af", marginBottom: 6 }}>
                What should you do?
              </div>
              <p style={{ fontSize: 13, color: "#6b7280", margin: "0 0 10px", lineHeight: "1.6" }}>
                The system has already applied <strong style={{ color: "#e2e8f0" }}>Bayesian resolution</strong> — 
                weighting values from higher-reliability sources (PHC 97%, ANM 90%) over lower ones (ASHA 65%).
                The resolved values above are what the pipeline has accepted.
              </p>
              <p style={{ fontSize: 13, color: "#6b7280", margin: 0, lineHeight: "1.6" }}>
                If you have ground-truth knowledge — for example, a physical register, lab report, or direct 
                communication with the field worker — you can override by contacting the relevant cadre 
                and updating their source record. This will be reflected in the next pipeline run.
              </p>
            </div>
          </>
        ) : (
          <div style={{ color: "#ef4444", fontSize: 13 }}>Could not load source data for this patient.</div>
        )}
      </div>
    </div>
  );
}

/* ── Source Reliability sidebar panel ── */
const SOURCE_META = {
  PHC:       { name: "PHC HMIS",         color: "#3b82f6" },
  ANM:       { name: "ANM Records",      color: "#10b981" },
  ASHA:      { name: "ASHA Records",     color: "#f59e0b" },
  ANGANWADI: { name: "Anganwadi ICDS",   color: "#a78bfa" },
};

/* ── Main Dashboard ── */
export default function Dashboard({ setPage }) {
  const [patients,     setPatients]    = useState(null);
  const [conflictSum,  setConflictSum] = useState(null);
  const [topConflicts, setTopConflicts] = useState([]);
  const [reliability,  setReliability] = useState([]);
  const [selected,     setSelected]    = useState(null);
  const [error,        setError]       = useState(false);

  useEffect(() => {
    Promise.all([
      api.get("/patients/summary"),
      api.get("/conflicts/summary"),
      api.get("/conflicts/?has_conflict=true&limit=6&page=1"),
      api.get("/reliability/"),
    ])
      .then(([p, c, cl, r]) => {
        setPatients(p.data);
        setConflictSum(c.data);
        setTopConflicts(cl.data.records || []);
        setReliability(r.data.sort((a, b) => b.source_reliability - a.source_reliability));
      })
      .catch(() => setError(true));
  }, []);

  if (error) return (
    <div style={{ color: "#ef4444", padding: 60, textAlign: "center", fontSize: 14 }}>
      ⚠️ Could not connect to backend. Make sure the FastAPI server is running on port 8000.
    </div>
  );

  const conflictRate = conflictSum && patients
    ? ((conflictSum.patients_with_conflicts / conflictSum.patients_analysed) * 100).toFixed(1)
    : null;

  const pieData = [
    { name: "High Risk", value: patients?.high_risk_patients || 0 },
    { name: "Normal",    value: patients?.normal_patients    || 0 },
  ];

  const barData = [
    { name: "Analysed",   value: conflictSum?.patients_analysed       || 0 },
    { name: "Conflicts",  value: conflictSum?.patients_with_conflicts  || 0 },
    { name: "High Risk",  value: patients?.high_risk_patients          || 0 },
  ];

  return (
    <>
      {selected && <ConflictModal item={selected} onClose={() => setSelected(null)} />}

      <div style={{ width: "100%" }}>
        {/* KPI row — all real backend values */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14, marginBottom: 24 }}>
          <KpiCard
            label="TOTAL PATIENTS"
            value={patients?.total_patients}
            color="#3b82f6"
            sub="Karnataka maternal cohort"
          />
          <KpiCard
  label="RESOLVED CONFLICTS"
  value={conflictSum?.resolved_conflicts}
  color="#10b981"
  sub="Supervisor approved"
/>
          <KpiCard
            label="PATIENTS WITH CONFLICTS"
            value={conflictSum?.patients_with_conflicts}
            color="#f59e0b"
            sub="At least 1 field disagreement"
          />
          <KpiCard
            label="CONFLICT RATE"
            value={conflictRate ? `${conflictRate}%` : null}
            color="#ef4444"
            sub="Of analysed patients"
          />
        </div>

        {/* Second row: High risk + normal */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 14, marginBottom: 24 }}>
          <KpiCard
            label="HIGH RISK MOTHERS"
            value={patients?.high_risk_patients}
            color="#ef4444"
            sub="Predicted by maternal risk model"
          />
          <KpiCard
            label="NORMAL RISK"
            value={patients?.normal_patients}
            color="#10b981"
            sub="No high-risk indicators"
          />
        </div>

        {/* Conflict Queue + Source Reliability */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 20, marginBottom: 24 }}>

          {/* Priority Conflict Queue — vertical, real data */}
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
              <div>
                <h2 style={{ fontSize: 17, fontWeight: 700, color: "white", margin: "0 0 3px" }}>
                  Priority Conflict Queue
                  <span style={{
                    background: "rgba(255,255,255,0.08)", color: "#9ca3af",
                    fontSize: 12, padding: "2px 10px", borderRadius: 20, marginLeft: 10,
                  }}>
                    {conflictSum?.patients_with_conflicts ?? "—"} cases
                  </span>
                </h2>
                <p style={{ fontSize: 12, color: "#4b5563", margin: 0 }}>
                  Showing top 6 · Karnataka · Click any card to review
                </p>
              </div>
              <button
                onClick={() => setPage && setPage("conflicts")}
                style={{
                  background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8, padding: "7px 14px",
                  color: "#9ca3af", fontSize: 12, fontWeight: 600, cursor: "pointer",
                }}
              >
                View All →
              </button>
            </div>

            {/* Vertical scroll list */}
            <div style={{
              display: "flex", flexDirection: "column", gap: 10,
              maxHeight: 480, overflowY: "auto",
              paddingRight: 4,
            }}>
              {topConflicts.length === 0 ? (
                <div style={{ color: "#4b5563", padding: 24, textAlign: "center" }}>Loading…</div>
              ) : (
                topConflicts.map((item, i) => (
                  <ConflictCard key={item.patient_id} item={item} index={i} onClick={setSelected} />
                ))
              )}
            </div>
          </div>

          {/* Source Reliability panel */}
          <div style={{ ...card, padding: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: "white", marginBottom: 4 }}>Source Reliability</div>
            <p style={{ fontSize: 11, color: "#4b5563", margin: "0 0 20px" }}>
              Mean reliability score per cadre (Bayesian weights)
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              {reliability.map((r, i) => {
                const meta = SOURCE_META[r.cadre] || { name: r.cadre, color: "#3b82f6" };
                const pct  = (r.source_reliability * 100).toFixed(1);
                return (
                  <div key={r.cadre}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <span style={{ fontSize: 11, color: "#4b5563", fontWeight: 700 }}>#{i + 1}</span>
                        <span style={{ fontSize: 13, color: "white", fontWeight: 600 }}>{meta.name}</span>
                      </div>
                      <span style={{ fontSize: 13, color: meta.color, fontWeight: 700 }}>{pct}%</span>
                    </div>
                    <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3, overflow: "hidden", marginBottom: 4 }}>
                      <div style={{
                        height: "100%", width: `${pct}%`,
                        background: meta.color, borderRadius: 3,
                        transition: "width 0.6s ease",
                      }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Charts */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div style={{ ...card, padding: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#e2e8f0", marginBottom: 4 }}>Risk Distribution</div>
            <p style={{ fontSize: 11, color: "#4b5563", margin: "0 0 16px" }}>
              {patients?.high_risk_patients} high risk · {patients?.normal_patients} normal
            </p>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} dataKey="value" outerRadius={75} innerRadius={40}
                  label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  <Cell fill="#ef4444" /><Cell fill="#10b981" />
                </Pie>
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "white", fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ display: "flex", gap: 16, justifyContent: "center" }}>
              {[{ l: "High Risk", c: "#ef4444" }, { l: "Normal", c: "#10b981" }].map(x => (
                <div key={x.l} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#6b7280" }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: x.c }} />{x.l}
                </div>
              ))}
            </div>
          </div>

          <div style={{ ...card, padding: 24 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#e2e8f0", marginBottom: 4 }}>Pipeline Overview</div>
            <p style={{ fontSize: 11, color: "#4b5563", margin: "0 0 16px" }}>
              {conflictSum?.patients_analysed} analysed · {conflictSum?.patients_with_conflicts} with conflicts · {patients?.high_risk_patients} high risk
            </p>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData} barSize={40}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: "#4b5563", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#4b5563", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "white", fontSize: 12 }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </>
  );
}