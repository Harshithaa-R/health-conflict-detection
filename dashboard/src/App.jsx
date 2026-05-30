import DashboardCards from "./components/DashboardCards";
import ReliabilityLeaderboard from "./components/ReliabilityLeaderboard";
import HighRiskPatients from "./components/HighRiskPatients";
import ConflictSummary from "./components/ConflictSummary";
import ConflictChart from "./components/ConflictChart";
import RiskChart from "./components/RiskChart";
import ReliabilityChart from "./components/ReliabilityChart";

function App() {

  return (
    <div style={{ padding: "30px" }}>

      <h1>
        Maternal Health Conflict Resolution Dashboard
      </h1>

      <DashboardCards />

      <br />

      <ReliabilityChart />

      <br />

      <ConflictChart />

      <br />

      <ConflictSummary />

      <br />

      <RiskChart />

      <br />

      <HighRiskPatients />

    </div>
  );
}

export default App;