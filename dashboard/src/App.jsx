import { useState, useEffect } from "react";
import Sidebar from "./components/layout/Sidebar";
import Topbar from "./components/layout/Topbar";
import Dashboard from "./pages/DashboardPage";
import Conflicts from "./pages/ConflictsPage";
import Patients from "./pages/Patients";
import Reliability from "./pages/ReliabilityPage";
import Analytics from "./pages/AnalyticsPage";
import Audit from "./pages/Audit";
import api from "./api/client";

const SIDEBAR_W = 260;

function App() {
  const [page, setPage]             = useState("dashboard");
  const [sidebarOpen, setSidebar]   = useState(true);
  const [conflictCount, setCount]   = useState(null);
  const [patientSummary, setSummary] = useState(null);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    api.get("/conflicts/count")
      .then(r => setCount(r.data.count))
      .catch(() => {});
    api.get("/patients/summary")
      .then(r => setSummary(r.data))
      .catch(() => {});
  }, []);

  // Notifications built from real pipeline output — NOT live data
  const notifications = patientSummary && conflictCount !== null ? [
    {
      id: 1,
      type: "conflict",
      title: "Conflict Detection Complete",
      body: `${conflictCount.toLocaleString()} patients have field-level disagreements across ASHA, ANM, PHC, and Anganwadi sources.`,
      urgent: true,
    },
    {
      id: 2,
      type: "pipeline",
      title: "Pipeline Run Complete",
      body: "All 8 stages passed. Bayesian resolution applied to 4,979 records across 10 Karnataka districts.",
      urgent: false,
    },
    {
      id: 3,
      type: "risk",
      title: "Maternal Risk Scoring Complete",
      body: `${patientSummary.high_risk_patients.toLocaleString()} high-risk mothers identified out of ${patientSummary.total_patients.toLocaleString()} patients.`,
      urgent: true,
    },
  ] : [];

  const sidebarWidth = sidebarOpen ? SIDEBAR_W : 64;

  const renderPage = () => {
    switch (page) {
      case "conflicts":   return <Conflicts />;
      case "patients":    return <Patients />;
      case "reliability": return <Reliability />;
      case "analytics":   return <Analytics />;
      case "audit":       return <Audit />;
      default:            return <Dashboard setPage={setPage} />;
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#090d14" }}>
      <Sidebar
        setPage={setPage}
        activePage={page}
        open={sidebarOpen}
        setOpen={setSidebar}
        conflictCount={conflictCount}
      />
      <div style={{
        marginLeft: sidebarWidth,
        width: `calc(100vw - ${sidebarWidth}px)`,
        minHeight: "100vh",
        background: "#090d14",
        overflowX: "hidden",
        transition: "margin-left 0.25s ease, width 0.25s ease",
      }}>
        <Topbar
          page={page}
          patientSummary={patientSummary}
          notifications={notifications}
          showNotifs={showNotifs}
          setShowNotifs={setShowNotifs}
        />
        <div style={{ padding: "28px" }} onClick={() => setShowNotifs(false)}>
          {renderPage()}
        </div>
      </div>
    </div>
  );
}

export default App;