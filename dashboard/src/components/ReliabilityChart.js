import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

export default function ReliabilityChart() {

  const data = [
    {
      source: "PHC",
      reliability: 0.983
    },
    {
      source: "ANM",
      reliability: 0.920
    },
    {
      source: "ANGANWADI",
      reliability: 0.769
    },
    {
      source: "ASHA",
      reliability: 0.669
    }
  ];

  return (
    <div
      style={{
        background: "white",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        marginTop: "20px"
      }}
    >
      <h2>Source Reliability</h2>

      <ResponsiveContainer
        width="100%"
        height={350}
      >
        <BarChart data={data}>

          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="source" />

          <YAxis domain={[0, 1]} />

          <Tooltip />

          <Bar
            dataKey="reliability"
            fill="#3b82f6"
          />

        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}