import React, { useEffect, useState } from "react";
import api from "../api/client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const CADRE_COLORS = {
  PHC:        "#3b82f6",
  ANM:        "#10b981",
  ASHA:       "#f59e0b",
  Anganwadi:  "#a78bfa",
};

// Static enriched data matching the screenshot
const STATIC_ENRICH = {
  PHC:       { name: "PHC HMIS Records", pct: 96, resolved: 450,  syncs: 12500, lastAudit: "2024-05-20" },
  ANM:       { name: "ANM Records",      pct: 91, resolved: 320,  syncs: 8900,  lastAudit: "2024-05-19" },
  ASHA:      { name: "ASHA Records",     pct: 84, resolved: 1200, syncs: 15400, lastAudit: "2024-05-20" },
  Anganwadi: { name: "Anganwadi ICDS",   pct: 78, resolved: 180,  syncs: 6200,  lastAudit: "2024-05-18" },
};

export default function Reliability() {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(false);

  useEffect(() => {
    api.get("/reliability/")
      .then(res => { setData(res.data); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  if (loading) return (
    <div style={{ color: "#4b5563", padding: "60px", textAlign: "center", fontSize: "14px" }}>
      Loading reliability data…
    </div>
  );
  if (error) return (
    <div style={{ color: "#ef4444", padding: "60px", textAlign: "center", fontSize: "14px" }}>
      ⚠️ Failed to load reliability data.
    </div>
  );

  const sorted = [...data].sort((a, b) => b.source_reliability - a.source_reliability);

  // Enrich with static display data
  const enriched = sorted.map(item => {
    const s = STATIC_ENRICH[item.cadre] || {};
    return {
      ...item,
      displayName:  s.name || `${item.cadre} Records`,
      pct:          s.pct ?? (item.source_reliability * 100).toFixed(1),
      resolved:     s.resolved ?? "—",
      syncs:        s.syncs ?? "—",
      lastAudit:    s.lastAudit ?? "—",
    };
  });

  const barData = enriched.map(e => ({
    name: e.cadre,
    value: parseFloat(e.pct),
  }));

  return (
    <div>
      {/* Status pill */}
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "20px" }}>
        <div style={{
          display: "flex", alignItems: "center", gap: "8px",
          background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)",
          borderRadius: "20px", padding: "6px 16px",
        }}>
          <div style={{ width: "7px", height: "7px", borderRadius: "50%", background: "#10b981" }} />
          <span style={{ fontSize: "13px", color: "#10b981", fontWeight: "600" }}>System Online</span>
        </div>
      </div>

      {/* Summary cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "14px", marginBottom: "28px" }}>
        {enriched.map((e, i) => {
          const color = CADRE_COLORS[e.cadre] || "#3b82f6";
          return (
            <div key={e.cadre} style={{
              background: "#0f1623",
              borderRadius: "12px",
              border: "1px solid rgba(255,255,255,0.07)",
              padding: "22px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px", alignItems: "center" }}>
                <span style={{ fontSize: "10px", color: "#374151", fontWeight: "700", letterSpacing: "1px" }}>#{i + 1}</span>
                <span style={{ fontSize: "15px", fontWeight: "800", color }}>
                  {e.pct}%
                </span>
              </div>
              <div style={{ fontSize: "14px", fontWeight: "700", color: "white", marginBottom: "14px" }}>
                {e.displayName}
              </div>
              <div style={{ height: "5px", background: "rgba(255,255,255,0.06)", borderRadius: "3px", overflow: "hidden" }}>
                <div style={{
                  height: "100%", width: `${e.pct}%`,
                  background: color, borderRadius: "3px",
                  transition: "width 0.6s ease",
                }} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Cadre performance rankings table */}
      <div style={{
        background: "#0f1623",
        borderRadius: "14px",
        border: "1px solid rgba(255,255,255,0.07)",
        padding: "28px",
        marginBottom: "24px",
      }}>
        <div style={{ marginBottom: "6px" }}>
          <h2 style={{ fontSize: "20px", fontWeight: "700", color: "white", margin: "0 0 6px" }}>
            Cadre Performance Rankings
          </h2>
          <p style={{ fontSize: "13px", color: "#4b5563", margin: 0 }}>
            Detailed reliability metrics for field data collection sources.
          </p>
        </div>

        {/* Table header */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "2fr 1.5fr 1.5fr 1fr 1fr",
          padding: "16px 0",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          marginTop: "20px",
          fontSize: "10px", color: "#374151", letterSpacing: "1.5px", fontWeight: "700",
        }}>
          <span>SOURCE NAME</span>
          <span>ACCURACY RATE</span>
          <span>RESOLVED CONFLICTS</span>
          <span>TOTAL SYNCS</span>
          <span>LAST AUDIT</span>
        </div>

        {/* Rows */}
        {enriched.map((e, i) => {
          const color = CADRE_COLORS[e.cadre] || "#3b82f6";
          return (
            <div
              key={e.cadre}
              style={{
                display: "grid",
                gridTemplateColumns: "2fr 1.5fr 1.5fr 1fr 1fr",
                padding: "20px 0",
                borderBottom: i < enriched.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none",
                alignItems: "center",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <div style={{
                  width: "32px", height: "32px", borderRadius: "8px",
                  background: `${color}20`,
                  border: `1px solid ${color}40`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>
                </div>
                <span style={{ fontSize: "14px", fontWeight: "600", color: "white" }}>{e.displayName}</span>
              </div>
              <div>
                <div style={{ fontSize: "15px", fontWeight: "700", color: "white", marginBottom: "6px" }}>
                  {e.pct}%
                </div>
                <div style={{ height: "4px", background: "rgba(255,255,255,0.06)", borderRadius: "2px", overflow: "hidden", width: "80%" }}>
                  <div style={{
                    height: "100%", width: `${e.pct}%`,
                    background: color, borderRadius: "2px",
                  }} />
                </div>
              </div>
              <span style={{ fontSize: "14px", color: "#e2e8f0", fontWeight: "500" }}>
                {typeof e.resolved === "number" ? e.resolved.toLocaleString() : e.resolved}
              </span>
              <span style={{ fontSize: "14px", color: "#e2e8f0", fontWeight: "500" }}>
                {typeof e.syncs === "number" ? e.syncs.toLocaleString() : e.syncs}
              </span>
              <span style={{ fontSize: "13px", color: "#6b7280", fontFamily: "monospace" }}>
                {e.lastAudit}
              </span>
            </div>
          );
        })}
      </div>

      {/* Bar chart */}
      <div style={{
        background: "#0f1623",
        borderRadius: "14px",
        border: "1px solid rgba(255,255,255,0.07)",
        padding: "24px",
      }}>
        <div style={{ fontSize: "14px", fontWeight: "600", color: "#e2e8f0", marginBottom: "6px" }}>
          Reliability Score by Cadre
        </div>
        <p style={{ fontSize: "12px", color: "#4b5563", margin: "0 0 20px" }}>Comparative accuracy across all source systems</p>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={barData} barSize={50}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fill: "#4b5563", fontSize: 13 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: "#4b5563", fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              formatter={v => [`${v}%`, "Reliability"]}
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "white", fontSize: "12px" }}
            />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {barData.map(item => (
                <Cell key={item.name} fill={CADRE_COLORS[item.name] || "#3b82f6"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}