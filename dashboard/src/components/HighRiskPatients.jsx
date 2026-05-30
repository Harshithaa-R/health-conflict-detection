import React from "react";

export default function HighRiskPatients() {

  const rows = [
    ["W00015", 8.4, 150, 112],
    ["W00027", 7.9, 162, 130],
    ["W00045", 8.2, 145, 155]
  ];

  return (
    <div>
      <h2>High Risk Patients</h2>

      <table border="1" cellPadding="10">

        <thead>
          <tr>
            <th>ID</th>
            <th>Hb</th>
            <th>BP</th>
            <th>Sugar</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((r) => (
            <tr key={r[0]}>
              <td>{r[0]}</td>
              <td>{r[1]}</td>
              <td>{r[2]}</td>
              <td>{r[3]}</td>
            </tr>
          ))}
        </tbody>

      </table>
    </div>
  );
}