import React from "react";

const PAGE_TITLES = {
  dashboard:   "Supervisor Dashboard",
  conflicts:   "Conflict Queue",
  patients:    "All Patients",
  reliability: "Source Reliability",
  analytics:   "Analytics Engine",
  audit:       "Audit Trail",
};

export default function Topbar({ page, patientSummary, notifications = [], showNotifs, setShowNotifs }) {
  const unread = notifications.filter(n => n.urgent).length;

  return (
    <div style={{
      height: 64,
      background: "#0d1117",
      borderBottom: "1px solid rgba(255,255,255,0.06)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 28px",
      position: "sticky",
      top: 0,
      zIndex: 10,
    }}>
      {/* Left: page title */}
      <span style={{ fontSize: 18, fontWeight: 700, color: "white", letterSpacing: "-0.3px" }}>
        {PAGE_TITLES[page] || "Dashboard"}
      </span>

      {/* Right: pipeline summary pills + bell */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>

        {/* Pipeline summary — replaces useless search bar */}
        {patientSummary && (
          <div style={{ display: "flex", gap: 8 }}>
            <div style={{
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 8, padding: "6px 14px",
              display: "flex", alignItems: "center", gap: 6,
            }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#3b82f6" }} />
              <span style={{ fontSize: 12, color: "#9ca3af" }}>
                <span style={{ color: "white", fontWeight: 600 }}>{patientSummary.total_patients.toLocaleString()}</span> patients
              </span>
            </div>
            <div style={{
              background: "rgba(239,68,68,0.08)",
              border: "1px solid rgba(239,68,68,0.2)",
              borderRadius: 8, padding: "6px 14px",
              display: "flex", alignItems: "center", gap: 6,
            }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#ef4444" }} />
              <span style={{ fontSize: 12, color: "#fca5a5" }}>
                <span style={{ fontWeight: 600 }}>{patientSummary.high_risk_patients.toLocaleString()}</span> high risk
              </span>
            </div>
            <div style={{
              background: "rgba(16,185,129,0.08)",
              border: "1px solid rgba(16,185,129,0.2)",
              borderRadius: 8, padding: "6px 14px",
              display: "flex", alignItems: "center", gap: 6,
            }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981" }} />
              <span style={{ fontSize: 12, color: "#6ee7b7" }}>
                <span style={{ fontWeight: 600 }}>Karnataka</span> · 10 districts
              </span>
            </div>
          </div>
        )}

        {/* Notification bell */}
        <div style={{ position: "relative" }}>
          <button
            onClick={e => { e.stopPropagation(); setShowNotifs(!showNotifs); }}
            style={{
              width: 36, height: 36, borderRadius: 8,
              background: showNotifs ? "rgba(59,130,246,0.15)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${showNotifs ? "rgba(59,130,246,0.4)" : "rgba(255,255,255,0.08)"}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              cursor: "pointer", position: "relative",
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            {unread > 0 && (
              <span style={{
                position: "absolute", top: 6, right: 6,
                width: 8, height: 8, borderRadius: "50%",
                background: "#ef4444", border: "1.5px solid #0d1117",
              }} />
            )}
          </button>

          {showNotifs && (
            <div onClick={e => e.stopPropagation()} style={{
              position: "absolute", top: 44, right: 0,
              width: 360,
              background: "#0f1623",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 12,
              boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
              zIndex: 100,
              overflow: "hidden",
            }}>
              <div style={{
                padding: "14px 16px",
                borderBottom: "1px solid rgba(255,255,255,0.06)",
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: "white" }}>Pipeline Alerts</span>
                <span style={{
                  background: "rgba(239,68,68,0.15)", color: "#fca5a5",
                  fontSize: 10, fontWeight: 700,
                  padding: "2px 8px", borderRadius: 10, border: "1px solid rgba(239,68,68,0.2)",
                }}>
                  {unread} require attention
                </span>
              </div>

              {notifications.map(n => (
                <div key={n.id} style={{
                  padding: "14px 16px",
                  borderBottom: "1px solid rgba(255,255,255,0.04)",
                  display: "flex", gap: 12,
                  background: n.urgent ? "rgba(239,68,68,0.03)" : "transparent",
                }}>
                  <div style={{
                    width: 34, height: 34, borderRadius: 8, flexShrink: 0,
                    background: n.type === "pipeline"
                      ? "rgba(16,185,129,0.15)"
                      : n.type === "risk"
                      ? "rgba(245,158,11,0.15)"
                      : "rgba(239,68,68,0.15)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    {n.type === "conflict" && (
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                      </svg>
                    )}
                    {n.type === "pipeline" && (
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    )}
                    {n.type === "risk" && (
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                      </svg>
                    )}
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "white", marginBottom: 3 }}>{n.title}</div>
                    <div style={{ fontSize: 12, color: "#6b7280", lineHeight: "1.5" }}>{n.body}</div>
                  </div>
                </div>
              ))}

              <div style={{ padding: "10px 16px" }}>
                <p style={{ fontSize: 11, color: "#374151", margin: 0, textAlign: "center" }}>
                  These alerts are generated from your pipeline run results, not real-time data.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}