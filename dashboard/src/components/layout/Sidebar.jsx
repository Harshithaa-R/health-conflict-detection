import React from "react";

const NAV = [
  {
    key: "dashboard",
    label: "Dashboard",
    icon: () => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
      </svg>
    ),
  },
  {
    key: "conflicts",
    label: "Conflict Queue",
    badge: true,
    icon: () => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    ),
  },
  {
    key: "patients",
    label: "All Patients",
    icon: () => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
    ),
  },
  {
    key: "reliability",
    label: "Source Reliability",
    icon: () => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    ),
  },
  {
    key: "analytics",
    label: "Analytics",
    icon: () => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="18" y1="20" x2="18" y2="10"/>
        <line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/>
      </svg>
    ),
  },
  {
    key: "audit",
    label: "Audit Trail",
    icon: () => (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="1 4 1 10 7 10"/>
        <path d="M3.51 15a9 9 0 1 0 .49-3.51"/>
      </svg>
    ),
  },
];

export default function Sidebar({ setPage, activePage, open, setOpen, conflictCount }) {
  return (
    <div style={{
      width: open ? 260 : 64,
      background: "#0d1117",
      borderRight: "1px solid rgba(255,255,255,0.06)",
      height: "100vh",
      position: "fixed",
      left: 0, top: 0,
      display: "flex",
      flexDirection: "column",
      transition: "width 0.25s ease",
      overflow: "hidden",
      zIndex: 20,
    }}>
      {/* Logo */}
      <div style={{
        padding: "20px 14px 16px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        display: "flex",
        alignItems: "center",
        justifyContent: open ? "space-between" : "center",
        minHeight: 64,
        gap: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10, flexShrink: 0,
            background: "linear-gradient(135deg,#3b82f6,#1d4ed8)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16, fontWeight: 800, color: "white",
          }}>H</div>
          {open && (
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "white", whiteSpace: "nowrap" }}>HealthSync</div>
              <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: "1.5px" }}>KARNATAKA HUB</div>
            </div>
          )}
        </div>
        {open && (
          <button onClick={() => setOpen(false)}
            style={{ background: "transparent", border: "none", cursor: "pointer", color: "#4b5563", padding: 4, flexShrink: 0 }}
            title="Collapse">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
        )}
        {!open && (
          <button onClick={() => setOpen(true)}
            style={{
              background: "transparent", border: "none", cursor: "pointer", color: "#4b5563",
              position: "absolute", bottom: 80, left: "50%", transform: "translateX(-50%)",
            }}
            title="Expand">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        )}
      </div>

      {open && (
        <div style={{ padding: "16px 20px 8px", fontSize: 10, color: "#374151", letterSpacing: "1.5px", fontWeight: 600 }}>
          MAIN NAVIGATION
        </div>
      )}

      {/* Nav items */}
      <div style={{ display: "flex", flexDirection: "column", gap: 2, padding: open ? "0 10px" : "8px 10px" }}>
        {NAV.map(({ key, label, icon, badge }) => {
          const isActive = activePage === key;
          const badgeNum = badge ? conflictCount : null;
          return (
            <button
              key={key}
              onClick={() => setPage(key)}
              title={!open ? label : undefined}
              style={{
                width: "100%",
                padding: open ? "10px 12px" : "10px",
                border: "none",
                borderRadius: 8,
                background: isActive ? "rgba(59,130,246,0.15)" : "transparent",
                color: isActive ? "#60a5fa" : "#6b7280",
                cursor: "pointer",
                textAlign: "left",
                fontSize: 14,
                fontWeight: isActive ? 600 : 400,
                display: "flex",
                alignItems: "center",
                gap: open ? 10 : 0,
                justifyContent: open ? "flex-start" : "center",
                position: "relative",
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  e.currentTarget.style.background = "rgba(255,255,255,0.04)";
                  e.currentTarget.style.color = "#9ca3af";
                }
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = isActive ? "rgba(59,130,246,0.15)" : "transparent";
                e.currentTarget.style.color = isActive ? "#60a5fa" : "#6b7280";
              }}
            >
              <span style={{ color: isActive ? "#60a5fa" : "#4b5563", flexShrink: 0 }}>{icon()}</span>
              {open && <span style={{ flex: 1 }}>{label}</span>}
              {open && badgeNum !== null && (
                <span style={{
                  background: "#ef4444", color: "white",
                  fontSize: 10, fontWeight: 700,
                  minWidth: 18, height: 18, borderRadius: 9,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  padding: "0 4px",
                }}>
                  {badgeNum > 9999 ? "9999+" : badgeNum}
                </span>
              )}
              {!open && badgeNum !== null && badgeNum > 0 && (
                <span style={{
                  position: "absolute", top: 6, right: 6,
                  width: 7, height: 7, borderRadius: "50%", background: "#ef4444",
                }} />
              )}
              {isActive && (
                <div style={{
                  position: "absolute", left: 0, top: "20%", bottom: "20%",
                  width: 3, borderRadius: "0 3px 3px 0", background: "#3b82f6",
                }} />
              )}
            </button>
          );
        })}
      </div>

      {/* User */}
      <div style={{
        marginTop: "auto",
        padding: open ? "12px 16px" : "12px 8px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        display: "flex", alignItems: "center", gap: 10,
        justifyContent: open ? "flex-start" : "center",
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%",
          background: "linear-gradient(135deg,#3b82f6,#1d4ed8)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 14, fontWeight: 700, color: "white", flexShrink: 0,
        }}>N</div>
        {open && (
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13, color: "white", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              District Health Officer
            </div>
            <div style={{ fontSize: 11, color: "#4b5563" }}>Karnataka</div>
          </div>
        )}
        {open && <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981", flexShrink: 0 }} />}
      </div>
    </div>
  );
}