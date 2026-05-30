import React from "react";

export default function ReliabilityLeaderboard() {

  const data = [
    ["PHC", 0.983],
    ["ANM", 0.920],
    ["ANGANWADI", 0.769],
    ["ASHA", 0.669]
  ];

  return (
    <div>
      <h2>Source Reliability</h2>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Source</th>
            <th>Reliability</th>
          </tr>
        </thead>

        <tbody>
          {data.map((row) => (
            <tr key={row[0]}>
              <td>{row[0]}</td>
              <td>{row[1]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}