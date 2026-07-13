import React, { useEffect, useState } from "react";
import api from "../api/client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell,
} from "recharts";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May"];

// Simulated monthly trend data
const TREND_DATA = MONTHS.map((m, i) => ({
  month: m,
  Identity:    [18, 25, 22, 38, 20][i],
  Measurement: [30, 40, 50, 65, 45][i],
  "Missing Data": [20, 35, 45, 55, 35][i],
  Temporal:    [12, 20, 28, 40, 22][i],
}));

const SEVERITY_DATA = [
  { name: "Critical", value: 12, color: "#ef4444" },
  { name: "High",     value: 28, color: "#f97316" },
  { name: "Medium",   value: 35, color: "#f59e0b" },
  { name: "Low",      value: 18, color: "#10b981" },
];

const BAR_COLORS = {
  Identity:       "#f59e0b",
  Measurement:    "#60a5fa",
  "Missing Data": "#34d399",
  Temporal:       "#818cf8",
};

function LiveChip() {
  return (
    <span style={{
      background: "rgba(16,185,129,0.15)",
      color: "#10b981",
      fontSize: "9px", fontWeight: "700",
      padding: "2px 7px", borderRadius: "4px", letterSpacing: "1px",
      display: "inline-flex", alignItems: "center", gap: "4px",
    }}>
      <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#10b981" }} />
      LIVE
    </span>
  );
}

function MetricCard({ icon, label, value, sub }) {
  return (
    <div style={{
      background: "#0f1623",
      border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: "12px", padding: "20px",
    }}>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "10px" }}>
        <LiveChip />
      </div>
      <div style={{ color: "#4b5563", marginBottom: "8px" }}>
        {icon}
      </div>
      <div style={{ fontSize: "10px", color: "#4b5563", letterSpacing: "1.5px", fontWeight: "600", marginBottom: "6px" }}>
        {label}
      </div>
      <div style={{ fontSize: "28px", fontWeight: "800", color: "white", marginBottom: "4px" }}>
        {value}
      </div>
      <div style={{ fontSize: "11px", color: "#4b5563" }}>{sub}</div>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)",
      borderRadius: "8px", padding: "12px",
    }}>
      <div style={{ fontSize: "12px", color: "#9ca3af", marginBottom: "8px" }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <div style={{ width: "8px", height: "8px", borderRadius: "2px", background: p.fill }} />
          <span style={{ fontSize: "12px", color: "white" }}>{p.name}: {p.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function Analytics() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get("/patients/summary").catch(() => null),
      api.get("/conflicts/summary").catch(() => null),
    ]).then(([p, c]) => {
      setSummary({ patients: p?.data, conflicts: c?.data });
    });
  }, []);

  return (
    <div>
      {/* Top charts row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: "20px", marginBottom: "20px" }}>

        {/* Conflict Trends */}
        <div style={{
          background: "#0f1623",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: "14px", padding: "28px",
        }}>
          <div style={{ marginBottom: "20px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: "700", color: "white", margin: "0 0 4px" }}>
              Conflict Trends
            </h3>
            <p style={{ fontSize: "12px", color: "#4b5563", margin: 0 }}>Monthly volume by classification class</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={TREND_DATA} barSize={12} barGap={2}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: "#4b5563", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#4b5563", fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
              <Legend
                wrapperStyle={{ paddingTop: "16px", fontSize: "12px" }}
                formatter={(value) => (
                  <span style={{ color: "#6b7280", fontSize: "12px" }}>{value}</span>
                )}
              />
              {Object.keys(BAR_COLORS).map(key => (
                <Bar key={key} dataKey={key} fill={BAR_COLORS[key]} radius={[3, 3, 0, 0]} stackId="a" />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Distribution */}
        <div style={{
          background: "#0f1623",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: "14px", padding: "28px",
        }}>
          <div style={{ marginBottom: "20px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: "700", color: "white", margin: "0 0 4px" }}>
              Severity Distribution
            </h3>
            <p style={{ fontSize: "12px", color: "#4b5563", margin: 0 }}>Current workload composition by priority</p>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={SEVERITY_DATA}
                dataKey="value"
                outerRadius={100}
                innerRadius={55}
                paddingAngle={3}
              >
                {SEVERITY_DATA.map(s => (
                  <Cell key={s.name} fill={s.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(v, name) => [v, name]}
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "white", fontSize: "12px" }}
              />
            </PieChart>
          </ResponsiveContainer>
          {/* Legend */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", justifyContent: "center" }}>
            {SEVERITY_DATA.map(s => (
              <div key={s.name} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: s.color }} />
                <span style={{ fontSize: "12px", color: "#6b7280" }}>{s.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Live metrics row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "14px" }}>
        <MetricCard
          icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>}
          label="AVG RESOLUTION TIME"
          value="4.2h"
          sub="-12% vs last week"
        />
        <MetricCard
          icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>}
          label="PATIENTS SCANNED"
          value={summary?.patients?.total_patients ? summary.patients.total_patients.toLocaleString() : "12,401"}
          sub="Karnataka Region"
        />
        <MetricCard
          icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>}
          label="DISTRICT COVERAGE"
          value="28/31"
          sub="Rural health units"
        />
        <MetricCard
          icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>}
          label="PIPELINE EFFICIENCY"
          value="94.2%"
          sub="Automated merging"
        />
      </div>
    </div>
  );
}